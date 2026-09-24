# 会话 Cookie 是怎么拿到的（自动，无需手动粘贴）

> 本文写于 2026-09-24，全部结论当天实测复现过。
> **先说清楚**：`cookie.txt` 不是手动粘贴进来的，是脚本从浏览器里读出来的。
> 早先 `script.md` 让读者"F12 复制 Cookie 整行"——**那句话是错的**，已改。

---

## 0. 结论

| 问题 | 答案 |
|---|---|
| 需要用户动手吗 | **不需要**。一次都不用 |
| 从哪读的 | 用户自己正在运行的 Chromium（ego lite），**用户本人的 profile** |
| 用的什么接口 | CDP `Network.getCookies`（浏览器层，不是页面层） |
| 为什么页面 JS 拿不到也能拿到 | `SESSION` 是 **HttpOnly**，`document.cookie` 读不到；但 CDP 是浏览器层调用，不看页面权限 |
| 怎么确认读对了 | 读出来之后和浏览器里的值做 sha256 比对，一致才算成功 |

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

### 4.2 它反转了一个常见判断

早先讨论"拿到别人的 cookie 难吗"时，我从服务端属性分析，说 HttpOnly 挡住了 XSS 路径。
那个结论本身没错，但**问错了对象**：

> 对攻击者来说，难点从来不是 cookie 本身，
> 而是**让代码跑进目标的浏览器上下文**。

而 agent 集成天生满足这个条件。所以真正该问的是"**谁能在这台机器上跑代码**"。

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
