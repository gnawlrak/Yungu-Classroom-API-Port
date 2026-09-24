# 会话 Cookie 是怎么拿到的

> 本文写于 2026-09-24，全部结论当天实测复现过。
> **先说清楚**：`cookie.txt` 不是手动粘贴进来的，是脚本从浏览器里读出来的。
> 早先 `script.md` 让读者"F12 复制 Cookie 整行"——**那句话其实没错**（Network 面板的
> 请求头里确实包含 `SESSION`），但我说它"根本拿不到"是夸大了，已改回。
> 手动并非不可能，只是麻烦；自动读取是为省事。

---

## 0. 结论

| 问题 | 答案 |
|---|---|
| 需要用户动手吗 | 走 CDP 这条路：**不需要**。一次都不用 |
| 从哪读的 | 用户自己正在运行的 Chromium（ego lite），**用户本人的 profile** |
| 用的什么接口 | CDP `Network.getCookies`（浏览器层，不是页面层） |
| 为什么页面 JS 拿不到也能拿到 | `SESSION` 是 **HttpOnly**，`document.cookie` 读不到；但 CDP 是浏览器层调用，不看页面权限 |
| 怎么确认读对了 | 读出来之后和浏览器里的值做 sha256 比对，一致才算成功 |
| **这是唯一的路吗** | **不是。** 见 §1.5 —— 有三条路，本文写的只是最方便的那条 |

---

## 1. 为什么能全自动拿到（三个条件缺一不可）

1. **浏览器以用户身份登录着** —— 会话已经存在，不需要我去登录
2. **agent 能附加到这个浏览器** —— ego-browser 提供 CDP 通道
3. **CDP 能读 HttpOnly cookie** —— `Network.getCookies` 返回整个 cookie 罐子，
   包括 JS 读不到的那些

第 3 条是关键。同一次实测里，两个口径的差异非常干净：

```
浏览器层 CDP 能看到:  cna, SESSION, UM_distinctid, cookie-language,
                      CNZZDATA1279258979, CNZZDATA1277820702      （6 个）
页面 document.cookie:  UM_distinctid, cookie-language, cna,
                      CNZZDATA1279258979, CNZZDATA1277820702      （5 个，无 SESSION）
```

`SESSION` 只在第一行里。**这就是"能自动拿到"和"只能手动粘贴"的分界线。**

### 1.5 三条路，门槛完全不同（重要）

本文只写了其中一条。**把本文当成充分条件是错的** —— 它绑定 ego-browser，
换个浏览器就跑不了。完整图景：

| 路 | 任意浏览器？ | 门槛 | 本文写了？ |
|---|---|---|---|
| **A. 调试端口（CDP）** | ❌ 只有 ego 这类专用浏览器 | 浏览器要专门开 CDP 通道。实测：普通 Chrome **默认不开**调试端口 | ✅ 就是本文 |
| **B. 浏览器扩展** | ✅ 任何 Chromium 浏览器 | 扩展申请 `cookies` 权限。`chrome.cookies.get` 本身就能读 HttpOnly，不需要任何"自动化" | ❌ 未写，见 §1.6 |
| **C. 读磁盘文件** | ✅ 任何浏览器 | 能读文件 + 解系统钥匙串 | ❌ 未写 |

**C 路走不通，这是实测的**（2026-09-24，本机）：

| 目标 | 真实读取 |
|---|---|
| Chrome `Default/Cookies` | ❌ Operation not permitted |
| Safari `History.db` | ❌ 拒绝 |
| `~/Library/Cookies/Cookies.binarycookies` | ❌ 拒绝 |
| `~/Library/Messages/chat.db` | ❌ 拒绝 |
| `~/Library/Mail/…` | ❌ 拒绝 |
| `~/yungu-tasks/cookie.txt` | ✅ 可读 |
| `~/.zsh_history` | ✅ 可读 |

**所以"写个 skill 就行了"是不成立的。** skill 跑在同一个进程、同一套权限里，
它是指令不是提权 —— shell 读不了的文件，skill 一样读不了。

> ⚠️ 顺带纠正一个我犯过的错：我最初用 `ls` 判断可达性，得出"Messages 可访问"的结论。
> 那是**假阳性** —— 某些目录上 `ls` 会返回成功但实际读不了。改用真实读取后才得到上表。

**A 路为什么能通：** CDP 是让 **Chrome 读它自己的数据**；C 路是让**另一个进程去碰
Chrome 的数据**。macOS TCC 拦的是跨进程，A 路不跨进程，所以 TCC 不出场。

**要让 C 路通**，需要用户在 系统设置 → 隐私与安全性 → 完全磁盘访问权限 里
把终端/agent 应用加进白名单。**这一步必须用户亲手点，且可见** ——
没有任何代码能自己开这个权限，这正是 macOS 设计这道闸门的目的。

### 1.6 给不懂技术的同学：有一个插件，但不在本仓库

有一个窄权限的浏览器插件，点一下就能导出 `SESSION`，不用碰开发者工具。

**它刻意不在本仓库发布**，只做小范围直接分发。原因见 README
「关于那个 Cookie 导出插件」一节 —— 简言之：一个"可直接运行的凭据提取工具"
挂在公开仓库里，改造成本接近零（换 `<all_urls>` + 三行外发代码就是木马），
而且它的安装说明本身在教"开开发者模式 + 加载未打包扩展"这个钓鱼最依赖的动作。

**"怎么做"和"为什么危险"公开是有价值的；提供一个开箱即用的提取器则不是。**

插件设计（需要的人可直接向作者取）：

| 项 | 值 |
|---|---|
| 权限 | `cookies` + `host_permissions: *://task.yungu.org/*` |
| cookie 读取 | 全代码仅一次：`chrome.cookies.get({url:"https://task.yungu.org/", name:"SESSION"})` |
| 网络请求 | **零**（grep 验证，无 fetch / XHR / sendMessage） |
| 数据出口 | 仅剪贴板 + 本地文件下载 |
| 未实测项 | `chrome.cookies.get` 在收窄权限下是否仍返回父域 cookie —— 构建环境无法加载未打包扩展，故未端到端验证。失败时把 `host_permissions` 改回 `*://*.yungu.org/*` 即可 |

---

## 2. `SESSION` 的实测属性

| 属性 | 实测值 | 含义 |
|---|---|---|
| `httpOnly` | **true** | 页面 JS 读不到 → XSS 偷会话这条路被堵 |
| `secure` | **false** | 不强制 HTTPS 通道，明文 HTTP 也可能携带 |
| `domain` | **`.yungu.org`** | 整个 yungu 产品族共享这一个会话，不限于 task 子域 |
| `Expires` / `Max-Age` | **无** | 浏览器会话 cookie，关浏览器即失效 |
| 值长度 | 36（UUID 形态） | 不可枚举/爆破 |
| 服务端 TTL | **未知**（未测） | 实测同一份 cookie 至少存活 8 天 |

> ⚠️ 文档里曾写"有效期约 1–2 周"，**那是没测过的猜测，已删除**。
> 现在只保留上面这些实测值，服务端 TTL 明确标为未知。

---

## 3. 可复现步骤

### 3.1 读出来

```bash
ego-browser nodejs <<'EOF'
const fs = await import("node:fs/promises");
const task = await taskSpace("read yungu session");
const page = task.page("p1");
await page.goto("https://task.yungu.org/", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(4000);

// 浏览器层读取全部 cookie —— 这一步能拿到 HttpOnly 的 SESSION
const all = await page.cdp("Network.getCookies", {});
const want = all.cookies
  .filter(c => /yungu/i.test(c.domain))
  .filter(c => ["SESSION", "cookie-language", "UM_distinctid",
                "CNZZDATA1277820702"].includes(c.name));

const header = want.map(c => `${c.name}=${c.value}`).join("; ");
await fs.writeFile("~/yungu-tasks/cookie.txt", header, { mode: 0o600 });
console.log("写入 %d 个键", want.length);
await task.finish({ keep: [] });
EOF
```

**不要打印 `header`。** 写文件就好，输出只报数量。

### 3.2 只保留需要的键

上面白名单里其实只有 `SESSION` 是认证必需的，其余是站点自己的语言/统计 cookie。
`cna` 和 `CNZZDATA1279258979` 可以不要——早先 `cookie.txt` 就是 4 个键，
说明当时就是按"够用就行"筛的。**少存一个键就少一分泄露面。**

### 3.3 验证读对了（必做）

读完之后一定要确认拿到的真是当前会话，而不是过期/错账号的：

```bash
python3 - <<'PY'
import hashlib, re
s = open("~/yungu-tasks/cookie.txt").read()
m = re.search(r'SESSION=([^;]+)', s)
print("cookie.txt 中 SESSION sha256[:12] =",
      hashlib.sha256(m.group(1).encode()).hexdigest()[:12] if m else "缺失")
PY
```

再在浏览器里跑一次 `Network.getCookies`，比对同一串 hash。
**一致才算成功**——这是唯一可靠的判据，"文件写成功了"不算。

更简单的功能校验：直接跑 `python3 yungu_tasks.py tasks`，能列出任务就是对的。

---

## 4. 安全含义（这部分比步骤重要）

### 4.1 这不只是"云谷"的事

同一台机器、同一个浏览器里，**你登录的任何站点**——钉钉、邮箱、任何东西——
都能用这一步拿到。`ego lite.app` 只要在跑，能力就是现成的。

但范围比这更大。真正该防的不是"谁能操纵你的浏览器"，而是
**"谁能在这台机器上执行代码"**：

- 浏览器只是最方便的那个入口，不是唯一的门
- §1.5 的 C 路（读文件）被 TCC 挡着，但那道闸门是**用户授权**才能开的
- 一旦某个工具/agent 拿到了执行权，它能自己找路，不需要本文

### 4.2 它反转了一个常见判断

早先讨论"拿到别人的 cookie 难吗"时，我从服务端属性分析，说 HttpOnly 挡住了 XSS 路径。
那个结论本身没错，但**问错了对象**：

> 对攻击者来说，难点从来不是 cookie 本身，
> 而是**让代码跑进目标的浏览器上下文**。

而 agent 集成天生满足这个条件。

### 4.3 叠加已知缺口，后果是完整的

`SESSION` 一旦到手，配合本仓库审计已确认的问题：

- 无敏感操作二次验证 → 拿到即全账号控制
- `studentIds` 不校验归属 → 能替他人提交
- `secure=false` + `.yungu.org` 全域共享 → 放大半径
- 服务端 TTL ≥ 8 天且无自动失效 → 泄露窗口很长

### 4.4 缓解

| 措施 | 说明 |
|---|---|
| 用完退出登录 | 让会话立即失效，别让 cookie 文件一直有效 |
| 别长期开着浏览器 | 不用时关掉 `ego lite.app` |
| 收紧文件权限 | `chmod 600 cookie.txt`，并确认 `.gitignore` 挡住了它 |
| 只存必需键 | 少一个键少一分面 |
| 谨慎授权浏览器访问 | 任何被授权碰浏览器的工具/扩展/agent，都继承你的**全部**登录态 |
| **更重要：别让凭据长期躺着** | `chmod 600` 挡的是**其他用户**，挡不住**以你身份运行的进程**。`cookie.txt` 在普通目录、不受 TCC 保护，任何进程都能静默读它。真正管用的是"不长期留" |

---

## 5. 什么时候该重新取

- 报告 `code:1000 请刷新！` → 会话失效，重新走一遍 §3
- 长时间没用过 → 主动退出再登录，别赌它还有效
- 换过账号 → 必须重取，否则会用错身份发请求

---

## 6. 相关

- 侦察方法与 CDP hook：`docs/recon-method.md`
- 脚本用法：`docs/script.md`
- 提交契约：`docs/api-submit.md`
- 接口安全审计（**未随仓库发布**，含复现细节）：本地 `docs/security-audit.md`
