# task.yungu.org 对外开放接口 · 侦察报告与剩余任务/课表读取

> 目标：找到 task.yungu.org 对外开放的 API，并能读到「剩余任务」与「课表」。
> 边界：**全程只读**，未使用任何鉴权绕过、口令爆破或漏洞利用。
> 接口名来自站点自己的**公开 CDN 前端产物**，数据读取只发生在**你自己的账号**会话下。

---

## 1. 结论速览

| 项 | 结论 |
|---|---|
| API 基址 | `https://task.yungu.org/api/<action>`（子应用另有前缀，见下） |
| 响应信封 | `{status, code, message, content, ifLogin, ifAdmin}` |
| 未登录统一返回 | `{"ifLogin":false,"status":false,"message":"请刷新！","code":1000,"content":null,"ifAdmin":false}` |
| 鉴权 | CAS SSO（`login.yungu.org`）；未登录时全站静态资源 **302 → CAS 登录** |
| 接口总数 | **1335** 个（跨 13 个服务前缀），按功能域归为 **19** 类 |
| 方法可判定率 | **94%**（GET 889 / POST 367 / PUT 3 / 未知 76）；只读 955 / 写操作 380 |
| 枚举方式 | 读前端 bundle：`cdn-assets.yungu.org/task/<版本>/index.js` + `<id>.async.js`，CDN **无需登录** |
| 「剩余任务」接口 | **`GET /api/getAllTasks`**（`inCludeTaskStatus=0`）＋ 计数 `GET /api/taskPublish/getTaskCountForStudent` |
| 「课表」接口 | **`GET /calendar/api/personal/schdedule/templateForPc`**（前缀 `/calendar/api/`，见 §2.4） |

### 发现 A：未登录时无法靠探测枚举接口

```
GET /api/                              -> code 1000 请刷新！
GET /api/zzz_definitely_not_exist_zzz  -> code 1000 请刷新！
GET /api/getAllTasks                   -> code 1000 请刷新！
```

鉴权过滤器**跑在路由之前**，路径是否存在不泄漏 —— "爆破接口名"在这站上是死路。
可行办法是读前端 bundle（公开产物），本报告与脚本采用的就是这条。

### 发现 B：`ifLogin:true` 不等于已登录

```
GET  /api/getDraftTasks -> {"ifLogin":true, "status":false, "code":1008, "message":"系统异常"}
POST /api/getDraftTasks -> {"ifLogin":false,"status":false, "code":1000, "message":"请刷新！"}
```

`getDraftTasks` 的 GET 路径未落在鉴权过滤器之后，直接落到处理器报"系统异常"，
**带不带 Cookie 都一样**。判定登录态必须以 `status:true` 为准。
> 这个坑是脚本自检时实测抓到的，`envelope_state()` 已按此修正。

---

## 2. 接口契约（已实测确认）

### 2.1 定位过程

1. 学生「任务」页 = 路由 `https://task.yungu.org/#/task`，实际渲染在同源 iframe `https://task.yungu.org/umiTask#/task`。
2. 该页的 bundle 是路由 chunk **`294.async.js`**，文案键：
   `taskList.willFinish=待完成`、`taskList.willCommit=待上交`、`taskList.HandedIn=已上交`
   → **「剩余任务」= 待完成 + 待上交**。
3. 从 iframe 的 `performance` 资源条目里读出它**真实发出的请求**（非猜测）：
   ```
   GET /api/getAllTasks?courseId=&includeContentLike=&inCludeTaskStatus=0&pageNum=1&pageSize=10&sortType=2
   GET /api/taskPublish/getTaskCountForStudent?courseId=
   ```

### 2.2 任务列表 `GET /api/getAllTasks`

| 参数 | 说明 |
|---|---|
| `inCludeTaskStatus` | **必填**（注意拼写是 `inClude`）。缺了会 `code 1008 系统异常` |
| `pageNum` / `pageSize` | 必填，缺了会 `code 1617 分页参数不能为空` |
| `courseId` / `includeContentLike` | 可留空 |
| `sortType` | `2` = 按截止时间排序 |

`inCludeTaskStatus` 实测语义：

| 值 | 含义 | 实测 total |
|---|---|---|
| `0` | **未完成（剩余任务）** | 2 |
| `1` | 全部历史（含逾期未交） | 625 |
| `2` | 已完成 | 805 |

响应结构：

```json
{"status":true,"code":0,"message":"操作成功","content":{
  "pageSize":50,"pageNum":1,"total":2,
  "data":[{"count":1,"groupName":"待修改","taskList":[ /* 任务对象 */ ]}]
}}
```

任务对象关键字段：
`title`、`courseName`、`doTaskStatus`(文本)、`doTaskStatusId`(编码)、`deadline`、
`deadlineTimeMillis`、`publishTime`、`expectFinishTime`、`taskDescription`、`ifTimeout`、
`taskPublishId`、`taskId`、`courseId`、`teamId`。
已见 `doTaskStatusId`：`1=未交` `2=已确认` `3=待修改`。

### 2.3 计数 `GET /api/taskPublish/getTaskCountForStudent?courseId=`

```json
{"status":true,"code":0,"content":{
  "totalCount":2, "dueTodayCount":1, "delayedCount":1, "allDelayedCount":1,
  "dueUpdateCount":1, "dueTomorrowCount":0, "dueRecentlyCount":0,
  "todayCount":0, "yesterdayCount":1, "earlierCount":1, "otherCount":0}}
```

---

### 2.4 课表 `GET /calendar/api/personal/schdedule/templateForPc`

「日程」（`https://task.yungu.org/#/calendar`，标题「我的日程」）是**同源子应用**
`https://task.yungu.org/newSchoolCalendar/#/index`；父应用埋点参数里
`submoduleName` 直接写着 **智能课表**，所以这条路是官方定位。

它真实发出的请求（同样从 iframe 的 `performance` 里读出来的，非猜测）：

```
GET /calendar/api/current/user                                            # 身份
GET /calendar/api/personal/schdedule/templateForPc?weekNumber=1
        &queryStartTime=1789315200000&queryEndTime=1789919999999          # 课表
```

> ⚠️ 路径里的 **`schdedule` 是站点自己拼错的**（正常应为 schedule），照抄才能命中。

| 参数 | 说明 |
|---|---|
| `weekNumber` | 周序号，从 1 开始（应用传当前周序号；实测传 1 也能取到当周数据） |
| `queryStartTime` / `queryEndTime` | 毫秒时间戳，窗口 = **本周一 00:00:00 → 本周日 23:59:59.999**（本地时区） |

响应结构：`content` 是**长度 7 的数组**（周一→周日），每个元素是该天的条目数组。

条目字段：

| 字段 | 说明 |
|---|---|
| `name` | 课程名 / 事项名（**课程名在 `name`，`courseName` 是 null**） |
| `startTime` / `endTime` | 毫秒时间戳（同一天的课有 40 分钟一节） |
| `playground` | 教室，如 `D421`、`足球场（沙坑）` |
| `teachers[]` | `{userId, userName, userEname, ...}` |
| `courseId` | **判断是不是真实课程的依据**：有值=课程；`起床/出寝/整理/午餐/放学/熄灯就寝` 等作息项为 null |
| `subjectName` / `weekDay` / `scheduleType` | 学科等附加信息 |

> 实测中 `courseId` 还会出现 `0`（如 `Club试课（体验）`、`十年级晚自修`）—— 非空即视为课程。

**一个数据观察（非解析错误）**：本周 2026-09-14~09-20 的数据里，周六为空，
而**周日 09-20 的 9 节课与周三 09-16 完全相同**（只有作息项文案不同：
周三 `Club试课（体验）`/`十年级晚自修`，周日 `社团`/`晚自习`）。
已逐条核对每天条目自带的时间戳与日期一致，确认是服务端返回的数据原样如此，
不是日期映射或解析 bug。至于学校为何这样排（调休/活动），本报告未作确认，不做猜测。

### 2.5 任务状态：能识别，但「逾期」是独立字段（不是状态）

`/api/getAllTasks` 返回的每条任务带这几个状态相关字段：

| 字段 | 取值 | 说明 |
|---|---|---|
| `doTaskStatus` | 未交 / 已确认 / 待修改 / 已交 | 状态文本 |
| `doTaskStatusId` | 1 / 2 / 3 / 4 | 状态编码，与左列一一对应 |
| `ifTimeout` | `true` / `false` / **`null`** | 是否逾期。**可能为 null，不能当 false 处理** |
| `over` | true / false | 任务本身是否已结束（结课） |

`doTaskStatusId` 是**全量枚举**结果（1432 条任务样本，无未知值、无遗漏）：

| id | `doTaskStatus` | 含义 |
|---|---|---|
| 1 | 未交 | 没交 |
| 2 | 已确认 | 交了且教师已确认 |
| 3 | 待修改 | 教师退回要求修改 |
| 4 | 已交 | 交了，等教师确认 |

**「逾期」不是一种状态，而是独立的 `ifTimeout` 布尔字段。** 站点 UI 用的是 6 态词表
（bundle i18n `homeworkManagement.status.*` 恰好 6 项：unsubmitted / overdueUnsubmitted /
pendingRevision / overdueSubmitted / onTimeSubmitted / teacherConfirmed），由两个字段合成：

| 派生标签 | 条件 | 实测条数 |
|---|---|---|
| 未交 | id=1，ifTimeout 非真 | 1 |
| 逾期未交 | id=1，ifTimeout=true | 234 |
| 准时提交 | id=4，ifTimeout 非真 | 527 |
| 逾期提交 | id=4，ifTimeout=true | 416 |
| 待修改 | id=3 | 1 |
| 教师已确认 | id=2 | 253 |

> **一个容易搞错的地方**：`ifTimeout=true` 的任务共 **709** 条，但派生标签里含「逾期」
> 字样的只有 **650** 条。差的 **59** 条是 `id=2 已确认 + ifTimeout=true` ——
> 已确认的显示优先级高于逾期。
> 所以「逾期」有两个口径：**客观字段 `ifTimeout=true`（709）** 与 **UI 标签（650）**，
> 二者不等价，用的时候要说清是哪个。

脚本对应支持：

```bash
python3 yungu_tasks.py tasks                          # 打印状态分布
python3 yungu_tasks.py tasks --overdue                # 按客观字段 ifTimeout 筛（709 口径）
python3 yungu_tasks.py tasks --group 逾期未交           # 按 UI 派生标签筛（650 口径之一）
python3 yungu_tasks.py tasks --group 待修改
python3 yungu_tasks.py tasks --verbose                # 显示 doTaskStatusId / ifTimeout / over
```

---

## 3. 实测样例（真实运行输出）

```
== 剩余任务计数  /api/taskPublish/getTaskCountForStudent ==
   剩余任务总数     2
   今天要交       1
   已逾期        1
   逾期合计       1

== 任务列表  /api/getAllTasks ==
   筛选 inCludeTaskStatus=0（未完成（剩余任务））  服务端 total=2  本次取回 2 条

   ── 待修改 ──
   Terminal Advanced         大学AI建模与算法 I   待修改   截止 09-11 22:00
   ── 今天要交 ──
   Worksheet and Student ID  大学AI建模与算法 I   未交     截止 09-16 22:00
```

课表（`python3 yungu_tasks.py timetable`，节选）：

```
身份：<学生姓名 Student Name>（student）
== 课表  2026-09-14 ~ 2026-09-20（共 7 天）==

   ── 2026-09-14 周一 ──
   08:00-08:40  大学AI建模与算法 I           D416-417   <教师姓名>/<教师姓名>
   08:45-09:25  语文 I                      D419       <教师姓名>
   10:00-10:40  荣誉物理 I                   D508       <教师姓名>
   13:50-14:30  H Academic English 2       D420       <Teacher>

   ── 2026-09-15 周二 ──
   08:00-08:40  大学软件工程 I                D421       <Teacher>/<教师姓名>
   08:50-09:30  体育 I                      足球场（沙坑）  <教师姓名>
   ...

   共 57 节（默认只列课程，加 --all 含作息项）
```

---

## 4. 用法

```bash
cd ~/yungu-tasks                      # 脚本目录（cookie.txt 与脚本同目录）

# 1) 取 Cookie：浏览器登录 https://task.yungu.org 后
#    F12 → Network → 任一 /api/ 请求 → Headers → Request Headers → 复制 Cookie 整行
echo '粘贴到这里' > cookie.txt
chmod 600 cookie.txt

# 2) 读剩余任务（默认 inCludeTaskStatus=0；自动使用同目录 cookie.txt，可零参数）
python3 yungu_tasks.py tasks
python3 yungu_tasks.py tasks --verbose          # 带 taskPublishId / 发布日 / 预计用时

# 3) 看全部历史 / 已完成
python3 yungu_tasks.py tasks --status 1 --page-size 100
python3 yungu_tasks.py tasks --status 2

# 4) 输出 JSON（便于接别的工具）
python3 yungu_tasks.py tasks --json

# 5) 课表（「日程」子应用）
python3 yungu_tasks.py timetable                 # 本周
python3 yungu_tasks.py timetable --week 1        # 下周（-1 = 上周）
python3 yungu_tasks.py timetable --date 2026-09-28   # 指定日期所在那周
python3 yungu_tasks.py timetable --all           # 连作息项（起床/出寝/午休…）一起列
python3 yungu_tasks.py timetable --json          # 输出 JSON

# 6) 各候选接口的返回一览
python3 yungu_tasks.py probe

# 7) 枚举全站接口
python3 yungu_tasks.py recon
python3 yungu_tasks.py recon --bundle-url https://cdn-assets.yungu.org/task/<版本>/index.js
```

会话来源优先级：`--cookie` > `--cookie-file` > 环境变量 `YUNGU_COOKIE` > 脚本同目录的 `cookie.txt`。
因此脚本可以放在任何位置、从任何 cwd 调用，只要 `cookie.txt` 与它同级。

---

## 5. 产物清单

全部产物位于 **`~/yungu-tasks/`**（自带 `.gitignore`，已忽略 `cookie.txt`）。

| 文件 | 说明 |
|---|---|
| `yungu_tasks.py` | 主脚本：`tasks` / `timetable` / `comments` / `probe` / `recon`，仅 Python 标准库 |
| `cookie.txt` | 你的会话凭据（`chmod 600`，已被 `.gitignore` 忽略，切勿提交/分享） |
| `docs/script.md` | **脚本使用文档**：四个子命令、全部选项、退出码、排错、扩展指南 |
| `docs/api-tasks.md` | **任务接口文档**：如何调用 + 如何解析（真实样例、49 个字段、状态口径、评论接口、可跑代码） |
| `docs/api-schedule.md` | **日程/课表接口文档**：如何调用 + 如何解析（时间窗算法、65 个字段、可跑代码） |
| `yungu_api_catalog.md` | 1335 个接口的完整目录（按功能域→模块分组 + 标注方法与写操作） |
| `docs/api-taxonomy.md` | **功能分类说明**：19 个功能域各能干什么 + 目录的两个固有缺口 |
| `docs/recon-method.md` | **API 侦察方法**：静态提取 + 动态 hook 的完整可跑配方（含 6 个踩过的坑） |
| `yungu_endpoints.json` | 同上机读版（含 method / service / module / mutating 字段） |
| `yungu_endpoints_discovered.json` | 脚本 `recon` 实跑输出（含 bundle 地址） |
| `docs/overview.md` | 项目总览（本文件） |

---

## 6. 注意事项

- **Cookie 即身份**，等同密码。别提交仓库、别贴群里；有效期约 1–2 周，过期重取即可。
- 脚本只发**只读查询**（GET / 空 body 的查询类 POST），不含提交、修改、删除任何操作。
- 站点有**多个接口前缀**：任务类走 `/api/...`，课表/日程走 `/calendar/api/...`
  （父应用调用子应用时用 `/leave/api/...` 这种形式）。所以 `recon` 列出的
  `/api/` 清单并不等于全部，子应用接口要按其前缀单独找。
- 课表时间窗按**本地时区**计算周一 00:00 → 周日 23:59:59.999。若机器时区不是
  Asia/Shanghai，`--week` 算出的窗口会偏，此时请用 `--date` 明确指定日期。
- 常见 `code`：`0` 成功、`1000` 未登录/会话失效、`1008` 业务异常（多为缺参数）、
  `1617` 分页参数不能为空、`9002` 参数不能为空、`1001` 用户无权限、`1039` 任务不存在。
- 只读取你自己账号的数据；读取他人数据需要相应授权。
