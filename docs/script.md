# 脚本文档：`yungu_tasks.py`

> task.yungu.org 剩余任务 / 课表读取与接口侦察。
> 单文件、**仅 Python 3 标准库**（无需 `pip install`），615 行。

---

## 1. 快速开始

```bash
cd ~/yungu-tasks

# 首次设置：把浏览器登录后的 Cookie 存成 cookie.txt（600 权限）
#   F12 → Network → 任一 /api/ 请求 → Headers → Request Headers → 复制 Cookie 整行
# 带守卫：已存在就跳过 —— 重复执行不会覆盖你现有的有效会话
if [ -s cookie.txt ]; then
  echo "cookie.txt 已存在，跳过（要更新请手动覆盖）"
else
  echo "请先手动创建：echo '你的Cookie' > cookie.txt && chmod 600 cookie.txt"
fi

python3 yungu_tasks.py tasks        # 看剩余任务
python3 yungu_tasks.py timetable    # 看本周课表
```

脚本会自动读取**与自己同目录**的 `cookie.txt`，所以放在哪、从哪个 cwd 调用都行。

---

## 2. 子命令总览

| 子命令 | 作用 | 会不会发请求 |
|---|---|---|
| `tasks` | 读「剩余任务」列表 + 计数 | 是（2 个只读接口） |
| `timetable` | 读「课表」（周视图） | 是（2 个只读接口） |
| `comments` | 读**任务评论**（含教师点评），标明归属任务 | 是（每任务 1 个只读接口） |
| `submit` | **上传成果并提交任务** | 默认不发；`--yes` 才写（需校方授权） |
| `probe` | 探测候选接口的 `code`/`message`/登录态 | 是（只读） |
| `recon` | 枚举全站对外开放的 `/api/` 接口 | 是（只读，下载前端 bundle） |

> 除 `submit` 外，脚本只发只读查询（GET / 空 body 的查询类 POST）。
> `submit` **默认 dry-run 一个字节都不发**，必须 `--yes` 才会真的写入；
> 它是本项目唯一的写操作入口，**使用前需确认持有校方授权**，契约见 `docs/api-submit.md`。

---

## 3. `tasks` — 剩余任务

```bash
python3 yungu_tasks.py tasks
```

输出分两段：

```
== 剩余任务计数  /api/taskPublish/getTaskCountForStudent ==
   剩余任务总数     2
   今天要交       1
   已逾期        1
   逾期合计       1
   待更新        1
   昨天新增       1
   更早         1

== 任务列表  /api/getAllTasks ==
   筛选 inCludeTaskStatus=0（未完成（剩余任务））  服务端 total=2  本次取回 2 条

   ── 待修改 ──
   Terminal Advanced                        大学AI建模与算法 I          待修改      截止 09-11 22:00
   ── 今天要交 ──
   Worksheet and Student ID                 大学AI建模与算法 I          未交       截止 09-16 22:00

   显示 2 / 2 条
   状态分布：待修改=1  未交=1
```

- 第一段是**计数接口**（便宜，只要数字时用它）
- 第二段是**列表接口**，按 `groupName`（待修改 / 今天要交 / list…）分组输出
- 每行：`任务标题 | 课程 | 派生状态 | 截止`；`[逾期]` 标记来自 `ifTimeout`

### 选项

| 选项 | 说明 |
|---|---|
| `--status {0,1,2}` | 服务端筛选。`0`=未完成（默认）`1`=全部历史（含逾期未交）`2`=已完成 |
| `--page-size N` | 每页条数，默认 `50`。想看全量历史用 `2000` |
| `--overdue` | 只列逾期任务（按**客观字段** `ifTimeout=true`） |
| `--group 标签` | 只看某个派生状态，如 `逾期未交` `待修改` `准时提交` `教师已确认` |
| `--verbose` | 追加 `doTaskStatusId` / `ifTimeout` / `over` / `taskPublishId` / `courseId` |
| `--json` | 追加打印 JSON（含 `derivedStatus` 与 `overdue` 字段） |
| `--dump 文件` | 把接口**原始响应**写到该文件 |

### 两个「逾期」口径（重要）

| 用法 | 口径 | 全站实测条数 |
|---|---|---|
| `--overdue` | 客观字段 `ifTimeout=true` | 709 |
| `--group 逾期未交` + `--group 逾期提交` | UI 派生标签 | 650 |

差的 59 条是「已确认 + ifTimeout=true」——**已确认的显示优先级高于逾期**。两个数不等价，用时说清口径。

---

## 4. `timetable` — 课表

```bash
python3 yungu_tasks.py timetable
```

```
身份：<学生姓名 Student Name>（student）
== 课表  2026-09-14 ~ 2026-09-20（共 7 天）==
   /calendar/api/personal/schdedule/templateForPc  weekNumber=1  window=1789315200000..1789919999999

   ── 2026-09-14 周一 ──
   08:00-08:40  大学AI建模与算法 I                    D416-417       <教师姓名>/<教师姓名>
   08:45-09:25  语文 I                           D419           <教师姓名>
   ...
   ── 2026-09-16 周三 ──
   08:00-08:40  大学软件工程 I                       D421           <Teacher>/<教师姓名>
   ...

   共 57 节（默认只列课程，加 --all 含作息项）
```

每行：`起-止时间 | 课程/事项 | 教室 | 教师`。

### 选项

| 选项 | 说明 |
|---|---|
| `--week N` | `0`=本周（默认）`1`=下周 `-1`=上周 |
| `--date YYYY-MM-DD` | 取该日期**所在那周**（跨时区/对齐周次时用它更稳） |
| `--all` | 连作息项一起列（起床/出寝/整理/体育活动大课间/午餐午休/放学/熄灯就寝…） |
| `--json` | 追加打印 JSON（按天分组） |
| `--dump 文件` | 原始响应落盘 |

### 只列课程 vs 全部

默认**只列真实课程**（判据是 `courseId is not None`），过滤掉作息项。
实测一周 118 条条目里，**57 条课程 / 61 条作息**。加 `--all` 看全部。

### 时间窗怎么算

课表接口要传**毫秒时间窗**。脚本按「**本周一 00:00:00 → 本周日 23:59:59.999**（本地时区）」计算，
已实测与站点自身传参**完全相等**（`1789315200000..1789919999999`）。

> ⚠️ 该算法依赖**本地时区**。本机是 `CST +0800`，若换到别的时区机器，
> `--week` 算出的窗口会偏 —— 此时用 `--date` 明确指定日期。

---

## 5. `comments` — 任务评论

查教师评论，并标明**评论属于哪个任务**。

```bash
python3 yungu_tasks.py comments
```

```
== 扫描任务 inCludeTaskStatus=0：2 个（服务端 total=2，--limit 可控）==

── Terminal Advanced
   taskPublishId=89939  taskId=701059  courseId=18348  课程=大学AI建模与算法 I  截止=09-11 22:00
   2026-09-16 12:32:58  <教师姓名>（老师）：【待修改】
   2026-09-16 12:29:05  <教师姓名>（老师）：Part 5 — Create hello_backup.py: What does ...

合计：1 个任务有评论，共 9 条
```

### 归属怎么保证

评论是**按 `taskPublishId` 逐个取的**，不是全局流，所以「哪条评论属于哪个任务」由接口本身决定；
脚本把每条评论输出在对应任务标题之下，标题取自接口返回的 `taskTitle`，避免张冠李戴。

### 选项

| 选项 | 说明 |
|---|---|
| `--status {0,1,2}` | 扫哪个档的任务，默认 `0`（剩余任务） |
| `--limit N` | 最多扫多少个任务，默认 `20`。**每个任务一次请求**，别设太大 |
| `--task ID[,ID]` | 只查指定任务（逗号分隔的 `taskPublishId`） |
| `--teacher-only` | 过滤掉自己发的，只看老师/他人的评论 |
| `--show-empty` | 连没有评论的任务也列出来 |
| `--json` | 额外输出 JSON |

### 示例

```bash
python3 yungu_tasks.py comments --status 2 --limit 15 --teacher-only   # 历史任务里的老师点评
python3 yungu_tasks.py comments --task 89939                            # 指定任务
python3 yungu_tasks.py comments --task 89939,90145 --json
```

### 「老师」是怎么判定的

接口**没有角色字段**。脚本用 `feedback[].userId != achievementUserResponse.userId` 判断：
相等标「（我）」，不等标「（老师）」。所以严格讲是"他人"，可能混入同学评论。
要精确到"哪一科的老师"，需再调 `/api/getMixedPublishDetail` 取 `mainTeachers[]` 比对（脚本暂未做）。

> `--task` 模式下没有任务列表数据，所以「课程」「截止」显示 `-`，
> 但 `taskTitle` / `taskId` / `courseId` / 评论内容都完整。

---

## 6. `submit` — 提交任务成果（唯一的写操作）

```bash
# 先看：默认 dry-run，不发任何请求
python3 yungu_tasks.py submit --task 91958 --file ./hw.pdf
```

```
== dry-run（未发送任何请求；确认无误后加 --yes）==

任务：test homework  (taskPublishId=91958)
  courseId=18349  taskUserRelationId=4458494  当前 achievementStatus=1  要求附件=True
  [dry-run] 将上传 ./hw.pdf → OSS 直传（sts/token → PUT OSS → upload_file/new）

将发送：POST /api/submitAchievementSendMessage
  {"courseId": 18349, "fileList": [11006958, "<fileId>"], "studentIds": [<student-id>],
   "teamList": null, "taskPublishId": 91958, "taskUserRelationId": 4458494, "textStatus": 0}

[dry-run] 未发送。加 --yes 才会真的提交。重交会新建版本，且无法自助删除旧版本。
```

### 选项

| 选项 | 说明 |
|---|---|
| `--task <id>` | 必填，`taskPublishId` |
| `--file <路径>` | 要上传的成果文件，可重复 |
| `--yes` | 真的发送。**缺省只 dry-run** |
| `--only-new` | 只带本次文件，不合并历史已上传附件（默认会合并，与应用行为一致） |
| `--drop-file <fileId>` | 从 `fileList` 剔除某个已交附件（可重复）——「删除」= 新版本不再包含它，旧版本仍在历史里 |
| `--text-status N` | `textStatus`，实测有附件提交时为 `0` |
| `--resubmit` | 允许对已交/已确认的任务重交（会新建成果版本） |
| `--skip-confirm` | 跳过交互二次确认（不建议） |
| `--sleep` / `--max-requests` | 沿用全局限流 |

### ⚠️ 撤回与重交（实测结论）

- **重交：随时可以，没有平台限制。** 实测在已交任务上重交成功，服务器不看状态、也不需要教师退回；
  每次重交**新建一个成果版本**（`achievementId` 变化），教师看到的是最新版。
- **撤回：做不到。** 没有接口能把自己改回「未交」；旧版本也不能自助删除。
- 所以脚本默认只对 `{未交, 待修改}` 放行 —— 这是**客户端的保守选择**，不是平台约束。
  确实要重交已交的成果：加 `--resubmit`。
所以上传本身是三步（取凭证 → OSS 签名 PUT → 注册元数据），并在最后**回读校验字节真的落地** ——
只做最后一步也能拿到 `fileId`，但文件是空的（实测踩过）。

脚本按这个顺序设卡，**每一步都在写入之前**：

1. 状态不在 `{1=未交, 3=待修改}` → 默认拒绝，需显式 `--resubmit`（服务器本身不拦，这是脚本的安全默认）
2. 任务要求附件但没给 `--file` → 拒绝
3. 身份字段缺任何一个 → **在上传之前**拒绝（避免在学校存储里留孤儿文件）
4. 无 `--yes` → 只打印 payload
5. 有 `--yes` 无 `--skip-confirm` → 要求交互输入 `yes`
6. 提交后**回读** `achievementStatus` 断言真的变了才报成功

### 为什么不能用 `submitCapture`

看接口名会以为提交走 `/api/capture/submitCapture` —— **那是教师端发布任务用的**。
学生提交实测是 `POST /api/submitAchievementSendMessage`。完整契约与抓包过程见 `docs/api-submit.md`。

---

## 7. `probe` — 接口探测

看各候选接口到底返回什么，用于人工判断/排查。

```bash
python3 yungu_tasks.py probe
```

```
endpoint                                       HTTP   结果
--------------------------------------------------------------------------------------------------------------
/api/getAllTasks                               200    成功（code=0, message=操作成功）  content{pageSize, pageNum, total, data}
/api/getTaskList                               200    成功（code=0, message=操作成功）  content{ing, beoverdue, complete, taskList}
/api/getDraftTasks                             200    调用异常（code=1001, message=用户无权限, ifLogin=True）
/api/getTaskDataCount                          200    调用异常（code=9002, message=参数不能为空, ifLogin=True）
/api/taskPublish/getTaskCountForStudent        200    成功（code=0, message=成功）  content{todayCount, yesterdayCount, ...}
```

| 选项 | 说明 |
|---|---|
| `--endpoint /api/xxx` | 只探这一个接口 |

> 成功判据是 `status:true`。`ifLogin:true` **不等于**调用成功（见下）。

---

## 8. `recon` — 枚举全站接口

```bash
python3 yungu_tasks.py recon
```

成果写入同目录的 `yungu_endpoints_discovered.json`（含 bundle 地址、全部接口、任务相关子集）。

| 选项 | 说明 |
|---|---|
| `--bundle-url URL` | 手动指定前端 bundle 地址（无会话时只能这样） |

怎么拿到 bundle 地址：F12 → Network → 找 `cdn-assets.yungu.org/task/<版本>/index.js`。

> **未登录时无法枚举接口**（实测）：鉴权过滤器跑在路由之前，
> `/api/随便什么` 与 `/api/真实接口` 返回**完全相同**的 `code:1000` 信封。
> 所以 `recon` 必须带会话，或手动给 `--bundle-url`。

---

## 9. 全局选项

### 会话（Cookie）

| 选项 | 说明 |
|---|---|
| `--cookie "SESSION=xxx; ..."` | 直接传 Cookie 请求头 |
| `--cookie-file 路径` | 从文件读 |
| （环境变量）`YUNGU_COOKIE` | 从环境变量读 |
| （自动兜底） | **脚本同目录的 `cookie.txt`** |

优先级：`--cookie` > `--cookie-file` > `YUNGU_COOKIE` > 同目录 `cookie.txt`。

```bash
# 覆盖默认会话，验证"未登录"分支是否正常
YUNGU_COOKIE="SESSION=fake" python3 yungu_tasks.py tasks
```

### 输出

| 选项 | 说明 |
|---|---|
| `--json` | 追加打印 JSON |
| `--verbose` | 打印更多字段 |
| `--dump 文件` | 把原始响应写文件（排查结构变化时最有用） |

---

## 10. 退出码

| 码 | 含义 |
|---|---|
| `0` | 成功 |
| `1` | `recon` 拿不到 bundle 地址 / 下载失败 |
| `2` | 缺会话、Cookie 文件读不了、接口调用失败，或 `submit` 被前置校验拒绝 |
| 其它 | `submit` 提交后回读状态未变化时返回 `2` |

可用于脚本串联：

```bash
python3 yungu_tasks.py tasks --json > /tmp/t.json || echo "取任务失败（见上方提示）"
```

---

## 11. 常见问题

### `!! 需要会话才能读取任务数据`

没找到 Cookie。按 §1 存 `cookie.txt`，或加 `--cookie-file` / `--cookie`。

### `!! 未登录 / 会话失效（code=1000, message=请刷新！）`

Cookie 过期（有效期约 **1–2 周**），重新从浏览器复制一份即可。

### `!! 任务列表调用失败：调用异常（code=1008, ...）`

多为缺必填参数。本脚本已带全参数（`inCludeTaskStatus` / `pageNum` / `pageSize`）；
若你手动改了接口要注意 `inCludeTaskStatus` 的**拼写**（大写 L）。

### `probe` 里 `getDraftTasks` 显示 `调用异常（code=1008, ifLogin=True）`

**正常现象**，不是脚本 bug。该接口的 GET 路径未落在鉴权过滤器之后，
无论带不带 Cookie 都返回 `ifLogin:true + code:1008`。脚本据此把成功判据定为 `status === true`。

### 课表里周日和周三的课一样

是**站点数据如此**，不是脚本 bug。已逐条核对每天条目自带的时间戳与日期一致，
周三/周日课程集合完全相同（仅作息项文案不同）。学校为何这样排本脚本不判断。

---

## 12. 内部结构（便于自己改）

### 函数职责

| 函数 | 作用 |
|---|---|
| `http_request(path, cookie, method, body)` | 最底层 HTTP，返回 `(状态码, 文本)`；HTTP 错误也返回正文以便读 JSON 报错 |
| `_decode(raw, headers)` | 按响应头/UTF-8/GBK 依次尝试解码 |
| `parse_json(text)` | 容错解析 JSON（允许前后有杂字符） |
| `envelope_state(payload)` | **唯一**的成功判据：返回 `(True/False/None, 说明)`，只认 `status:true` |
| `call(path, cookie, params, method, body)` | 拼 query/body → 发请求 → 拆信封，返回 `(信封, 说明, 状态码, 原文)` |
| `session_required(args)` | 无会话时打印指引并返回 False |
| `flatten(content)` | 任务列表 `data[].taskList[]` **两层摊平**（关键） |
| `derive_status(task)` | 由 `doTaskStatusId` + `ifTimeout` 合成 UI 六态标签 |
| `is_overdue(task)` | `ifTimeout is True`（**三态字段**，不能当真值判断） |
| `week_window(offset, date)` | 算周一日期与毫秒时间窗 |
| `resolve_cookie(args)` | 四级会话来源解析 |
| `fetch_achievement(cookie, taskPublishId)` | 取任务成果详情（含评论），**内部走 POST + JSON body** |
| `upload_file(path, cookie)` | 上传成果文件（STS 凭证 → OSS 签名 PUT → 注册元数据 → **回读校验**），返回 `fileId` |
| `cmd_tasks` / `cmd_timetable` / `cmd_comments` / `cmd_submit` / `cmd_probe` / `cmd_recon` | 六个子命令 |

### 关键常量

```python
LIST_ENDPOINT       = "/api/getAllTasks"
COUNT_ENDPOINT      = "/api/taskPublish/getTaskCountForStudent"
CAL_USER_ENDPOINT   = "/calendar/api/current/user"
TIMETABLE_ENDPOINT  = "/calendar/api/personal/schdedule/templateForPc"   # schdedule = 站点拼写
ACHIEVEMENT_ENDPOINT= "/api/student/getAchievementDetail"                # 含评论，必须 POST
STATUS_MODES        = {"0": "未完成（剩余任务）", "1": "全部历史", "2": "已完成"}
DO_STATUS_ID        = {1: "未交", 2: "已确认", 3: "待修改", 4: "已交"}
DERIVED_STATUS      = {...}   # (id, 是否逾期) -> 六态标签
```

---

## 13. 加一个新接口/新子命令

按 §10 的结构照抄即可，套路是固定的：

1. **找到接口**：让应用自己告诉你，别猜 ——
   在已登录页面里读同源 iframe 的真实请求：

   ```javascript
   // 浏览器控制台（或在 ego-browser 的 page.evaluate 里）
   const ifr = document.querySelector("iframe");
   ifr.contentWindow.performance.getEntriesByType("resource")
      .map(e => e.name).filter(n => n.indexOf("/api/") >= 0);
   ```

2. **加常量**：把路径按上面的常量区加进去（**注意子应用前缀**，如 `/calendar/api/`）。
3. **写 `cmd_xxx`**：用 `call()` 发请求，用 `env["status"] is True` 判成功，
   失败时打印 `note`（里面已带 `code` 和 `message`）。
4. **加进 `main()`** 的 `choices` 和分发表：

   ```python
   ap.add_argument("command", choices=["tasks", "timetable", "probe", "recon", "xxx"])
   return {"tasks": cmd_tasks, ..., "xxx": cmd_xxx}[args.command](args)
   ```

5. **验证**：先 `--dump` 落盘看原始结构，再写解析；不要凭猜写字段名。

---

## 14. 相关文档

| 文件 | 内容 |
|---|---|
| `docs/api-tasks.md` | 任务接口契约（参数、49 字段、状态口径、**评论接口**、解析代码） |
| `docs/api-schedule.md` | 日程/课表接口契约（时间窗算法、65 字段、解析代码） |
| `docs/api-submit.md` | **提交成果接口契约**（上传→提交→回读，含撤回边界） |
| `yungu_api_catalog.md` | 1345 个接口全量目录（标注方法与写操作） |
| `docs/api-taxonomy.md` | 接口功能分类：19 个功能域各能干什么 |
| `docs/recon-method.md` | API 侦察方法：静态提取 + 动态 hook 的完整配方 |
| `README-yungu.md` | 项目总览：侦察过程、发现、注意事项 |
