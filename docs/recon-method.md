# API 侦察方法（可复用配方）

> 本文记录**怎么找出 task.yungu.org 的私有接口**。所有代码块都实跑验证过。
> 核心思想：**让应用自己在你的会话里发请求，然后读它的请求** —— 不猜、不爆破。
> 边界：**侦察阶段全程只读** —— 只记录应用自己发出的请求，不发送自造请求。
> 380 个写接口中只有 1 个后来被实现为功能（`submitAchievementSendMessage`，
> 是在教师专门创建的测试任务上实测的），其余一律不调用。

---

## 0. 两条路，配合用

| | 静态提取 | 动态观测 |
|---|---|---|
| 做法 | 下载前端 bundle 扫路径字面量 | 在你已登录的页面里 hook 请求 |
| 拿到 | **全量清单** + HTTP 方法 | **真实参数/body** + 调用时机 |
| 覆盖 | 字面量路径（下界） | 实际发生过的调用 |
| 成本 | 一次下载 | 每类页面点一遍 |

**先静态扫出清单，再动态确认怎么调。** 单靠任一条都会漏。

---

## 1. 静态提取：从公开 bundle 扫接口

前端产物放在 **CDN 上，不需要登录**：`cdn-assets.yungu.org/task/<版本>/index.js`。

### 1.1 先定位 bundle 地址

**注意路径是 `/` 根路径，不是 `/umiTask`** —— 后者只返回登录壳页，里面没有 bundle 引用（这是个实测踩过的坑）。

```bash
COOKIE="$(cat ~/yungu-tasks/cookie.txt)"
curl -s -H "Cookie: $COOKIE" -H "Referer: https://task.yungu.org/" \
  "https://task.yungu.org/" \
  | grep -oE '//cdn-assets\.yungu\.org/task/[0-9]+/index\.js' | head -1
```

输出形如 `//cdn-assets.yungu.org/task/20260916191038/index.js`（补上 `https:` 即可）。

> 无会话时入口页会 302 到 CAS 登录中心，拿不到地址。

**版本号会变**（站点重新部署时会换），但**代码不一定变**。实测对比两个相邻构建：
文件大小完全相同、接口集合 1208 vs 1208（增 0 删 0），**全文只差 4 个字符**
（内嵌的 `o.p="//cdn-assets.yungu.org/task/<版本>/"`）。
所以旧版本扫出的接口清单通常仍然有效，但**重新部署后建议复核一次**：

```bash
# 两个版本的接口集合差异（把 <旧> <新> 换成实际版本号）
for v in 20260916175936 20260916191038; do
  curl -s -o /tmp/b_$v.js "https://cdn-assets.yungu.org/task/$v/index.js"
done
python3 - <<'PY'
import re
P = r'(?:/[A-Za-z][A-Za-z0-9-]*)?/api/[A-Za-z0-9_/.-]{1,140}'
def eps(p):
    t = open(p, encoding='utf-8', errors='replace').read()
    return {m.rstrip('.,;') for m in re.findall(P, t) if re.search(r'/api/.', m)}
a, b = eps('/tmp/b_20260916175936.js'), eps('/tmp/b_20260916191038.js')
print("旧", len(a), "新", len(b), "新增", len(b - a), "移除", len(a - b))
PY
```

### 1.2 扫路径字面量 + 提取方法

```python
import re, json, urllib.request

BUNDLE = "https://cdn-assets.yungu.org/task/20260916175936/index.js"
req = urllib.request.Request(BUNDLE, headers={"User-Agent": "Mozilla/5.0"})
t = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
print("bundle 大小:", len(t), "字符")

# 路径字面量（保留子应用前缀！）
P = r'(?:/[A-Za-z][A-Za-z0-9-]*)?/api/[A-Za-z0-9_/.-]{1,140}'
eps = set()
for m in re.findall(P, t):
    e = m.rstrip(".,;")
    if re.search(r"/api/.", e) and not e.rstrip("/").endswith("/api"):
        eps.add(e)

# 方法：从应用自身的调用点读
meth = {}
for m in re.finditer(r'"(' + P + r')"\s*,\s*\{\s*method\s*:\s*"([A-Z]+)"', t):
    meth[m.group(1)] = m.group(2)
for m in re.finditer(r'"(' + P + r')\?"\s*\.concat', t):
    meth[m.group(1)] = "GET(querystring)"

print("index.js 内接口:", len(eps), " 有方法信息:", len(meth))
print("\n任务相关样例：")
for e in sorted(x for x in eps if re.search(r"task|homework|draft|capture", x, re.I))[:15]:
    print("  %-6s %s" % (meth.get(e, "?"), e))
```

### 1.3 把 chunk 下全（关键，最容易漏）

主包里有 webpack 的 chunk 声明表，**必须解析它**，否则会漏掉大量接口：

```python
import re, urllib.request

BUNDLE = "https://cdn-assets.yungu.org/task/20260916175936/index.js"
t = urllib.request.urlopen(urllib.request.Request(
        BUNDLE, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8", "replace")

# 主包声明：o.e=function(e){...0!==r[e]&&{0:1,1:1,...}}
m = re.search(r"0!==r\[e\]&&\{([0-9:,]+)\}", t)
declared = sorted({int(x) for x in re.findall(r"(\d+):", m.group(1))}) if m else []
print("声明 chunk 数:", len(declared), " 最大 id:", declared[-1] if declared else None)
print("→ 再逐个下载 <id>.async.js 扫一遍（本次实测下载 716 个文件）")
```

---

## 2. 动态观测：抓到真实参数（决定性的一步）

三步，**缺一不可**。下面这段可直接跑（会自己开浏览器、自己关闭）：

```bash
ego-browser nodejs <<'EOF'
const task = await taskSpace("api recon");
const page = task.page("p1");

// ① 在应用代码之前注入钩子：fetch + XHR 都记，含 method 和 body
await page.cdp("Page.enable");
await page.cdp("Page.addScriptToEvaluateOnNewDocument", { source: `
window.__req=[];
(function(){
  function rec(m,u,b){ try{ window.__req.push({m:m,u:u,b:(b==null?"":String(b).slice(0,400))}); }catch(e){} }
  var _f = window.fetch;
  window.fetch = function(){
    var a=arguments[0], i=arguments[1]||{};
    rec(i.method||"GET", (typeof a==="string"?a:(a&&a.url)), i.body);
    return _f.apply(this, arguments);
  };
  var _o = XMLHttpRequest.prototype.open, _s = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function(m,u){ this.__m=m; this.__u=u; return _o.apply(this,arguments); };
  XMLHttpRequest.prototype.send = function(b){ rec(this.__m, this.__u, b); return _s.apply(this,arguments); };
})();` });

// ② 必须先离开该 origin —— 否则 hash 导航不会重载文档，钩子根本装不上
await page.goto("about:blank");
await page.goto("https://task.yungu.org/#/task");
await page.waitForLoadState();
await page.waitForTimeout(9000);

// ③ 用客户端路由切到目标页（钩子仍在），然后逐个 frame 读（钩子在每个 frame 自己的 window 里）
await page.evaluate(() => {
  const els = [...document.querySelectorAll("a,li,div,span")]
    .filter((x) => (x.innerText || "").trim() === "日程");
  if (els.length) (els[els.length - 1].closest("a") || els[els.length - 1]).click();
});
await page.waitForTimeout(10000);

const out = await page.evaluate(() => {
  const collect = (w) => { try { return (w.__req || []); } catch (e) { return []; } };
  let all = collect(window);
  [...document.querySelectorAll("iframe")].forEach((f) => { all = all.concat(collect(f.contentWindow)); });
  const seen = new Set(), res = [];
  all.filter((r) => r.u && r.u.indexOf("/api/") >= 0).forEach((r) => {
    const k = r.m + " " + r.u;
    if (!seen.has(k)) { seen.add(k); res.push(r); }
  });
  return res;
});
console.log("捕获 " + out.length + " 个接口：");
out.forEach((r) => console.log("  " + r.m + " " + r.u.replace("https://task.yungu.org", "") + (r.b ? "\n      BODY: " + r.b : "")));
await task.finish({ keep: [] });
EOF
```

### 为什么必须这么做（三个坑的成因）

| 坑 | 现象 | 原因 |
|---|---|---|
| 用 `page.evaluate` 装钩子 | 抓不到任何请求 | 装得太晚，应用已经加载完 |
| 直接 `goto` 目标 hash | 钩子没装上 → 0 捕获 | **hash 导航不触发文档重载**，脚本不会重新注入 |
| 只读顶层 `window.__req` | 明明有请求却是 0 | 钩子在**每个 frame 自己的 window** 里执行，iframe 的请求不在顶层 |

### 轻量替代：读 `performance`

不用注入时，可以直接读同源 iframe 的资源条目（拿不到 POST body，且个别页面会空）：

```javascript
const ifr = document.querySelector("iframe");
ifr.contentWindow.performance.getEntriesByType("resource")
   .map(e => e.name).filter(n => n.indexOf("/api/") >= 0);
```

---

## 3. 确认响应结构

拿到"地址 + 参数"后，用会话直接调，落盘原始响应再看字段：

```bash
python3 yungu_tasks.py tasks --dump /tmp/raw.json    # 换成目标接口
```

判据（**这条最容易被骗**）：

```
只有 status === true 才算成功
ifLogin === true 不代表调用成功（GET /api/getDraftTasks 就带 ifLogin:true + code:1008）
```

---

## 4. 交叉验证（别单点采信）

1. **页面文本 vs JSON**：页面渲染出的值，与接口返回逐字段比对
2. **列表 vs 详情**：列表里的标题，与详情接口返回的 `taskTitle` 比对
3. **自算 vs 应用传参**：例如课表时间窗，自算 `1789315200000..1789919999999`，与应用实际传的完全相等
4. **两份独立实现**：手工脚本与正式脚本各自跑一遍，数字应一致

---

## 5. 我踩过的六个坑（都造成过错误结论）

| # | 坑 | 后果 |
|---|---|---|
| 1 | 正则不保留子应用前缀，`/calendar/api/x` 记成 `/api/x` | 目录里出现 **202 条幻影**接口 |
| 2 | 过滤条件写成 `count('/') >= 3` | **漏掉 204 个单段接口**（`/api/saveCommentary` 等） |
| 3 | 只下 id 1..340 的 chunk | **漏 377 个 chunk**，接口少算 62 个 |
| 4 | 直接 grep 中文文案 | **0 命中** —— bundle 里是 `\uXXXX` 转义 |
| 5 | hash 导航后期望钩子生效 | 钩子装不上 → 0 捕获（见 §2） |
| 6 | 只读顶层 `window.__req` | iframe 的请求全丢（见 §2） |

**教训：每次得到新数字，都要用另一种方法复核一遍再报。** 本次接口数在
1265 → 1069 → 1273 → 1335 之间反复修正过，每一次都是复核发现的。

---

## 6. 抓不到的（方法的固有边界）

| 缺口 | 例子 | 原因 |
|---|---|---|
| 动态拼接的路径 | `/api/student/getAchievementDetail` | bundle 里只有 `/api/teacher/getAchievementDetail` 是字面量，学生版运行时拼 |
| 独立 bundle 的子应用 | `/calendar/api/personal/schdedule/templateForPc` | 日程子应用 `newSchoolCalendar` 有自己的产物 |
| 未触发过的调用 | —— | 没点到的页面/按钮，请求就不会发生 |

→ 静态清单是**下界**。要确认某接口存在，以**动态观测**为准。

---

## 7. 安全边界

- 侦察阶段只记录请求，不发送自造请求；**380 个写接口中只有 1 个被实现为功能**
  （`submitAchievementSendMessage`，在教师建的测试任务上实测），其余一律不调用
- 会话：只用自己的 `cookie.txt`（600，已 gitignore）
- 不猜参数去试探写接口——那是越界，也拿不到可靠结论
- 站点压力：批量调用时加 `sleep`、设上限（脚本默认 `--max-requests 300`）

---

## 8. 相关文件

| 文件 | 内容 |
|---|---|
| `docs/script.md` | 脚本用法与内部结构 |
| `docs/api-tasks.md` | 任务 + 评论接口契约 |
| `docs/api-schedule.md` | 课表接口契约 |
| `docs/api-taxonomy.md` | 1335 个接口的功能分类 |
| `yungu_tasks.py` | 可直接沿用的 `call()` / `envelope_state()` |
