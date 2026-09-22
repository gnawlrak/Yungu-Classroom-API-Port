# 任务接口文档（task.yungu.org）

> 本文件覆盖「我的任务」（路由 `https://task.yungu.org/#/task`）用到的接口。
> 所有请求/响应样例均为**实测抓取**（你自己的学生账号，2026-09-16），非推测。
> 只读接口，不含任何提交/修改操作。

---

## 0. 接口清单

| # | 方法 | 路径 | 用途 | 验证状态 |
|---|---|---|---|---|
| 1 | `GET` | `/api/getAllTasks` | **任务列表**（按状态/课程筛选，分页，按截止时间排序） | ★ 实测通过 |
| 2 | `GET` | `/api/taskPublish/getTaskCountForStudent` | **任务计数**（今天要交/已逾期/总数…） | ★ 实测通过 |
| 3 | `POST` | `/api/student/getAchievementDetail` | **任务详情 + 评论**（含教师评论、提交文件、captureId） | ★ 实测通过 |
| 4 | `GET` | `/api/getMixedPublishDetail` | 任务元信息（课程/标题/学生/教师/附件，**不含评论**） | ★ 实测通过 |
| 5 | `GET` | `/api/getTaskList` | 任务列表（另一种聚合结构，含 ing/beoverdue/complete） | ◐ 实测有响应，未使用 |
| 6 | `GET` | `/api/getTaskDataCount` | 任务计数（需额外参数） | ◐ 实测需参数 |
| 7 | `POST` | `/api/getDraftTasks` | 草稿箱任务 | ✗ 学生账号返回无权限 |

> ★ = 已用真实数据验证；◐ = 调用有响应但未完整验证；✗ = 该账号无权限。

---

## 1. 通用约定

### 1.1 鉴权

CAS SSO。所有请求需要带浏览器里登录后的 **Cookie 请求头**：

```bash
COOKIE="$(cat ~/yungu-tasks/cookie.txt)"     # 形如 SESSION=xxx; cookie-language=zh
```

未登录 / 会话过期时，**所有**接口返回同一个信封（HTTP 仍是 200）：

```json
{"ifLogin":false,"status":false,"message":"请刷新！","code":1000,"content":null,"ifAdmin":false}
```

### 1.2 统一响应信封

```json
{"ifLogin": true, "status": true, "message": "操作成功", "code": 0,
 "content": { ... }, "ifAdmin": false}
```

| 字段 | 类型 | 含义 |
|---|---|---|
| `status` | bool | **是否成功。只有 `status:true` 才算成功** |
| `code` | int | 业务码，`0` = 成功 |
| `message` | string | 提示语（中文） |
| `content` | object/array/null | 实际数据，结构随接口而异 |
| `ifLogin` | bool | 是否已登录。**注意 `true` 不等于调用成功**，见 §1.4 |
| `ifAdmin` | bool | 是否管理员 |

### 1.3 错误码（实测）

| code | message | 触发条件 |
|---|---|---|
| `0` | 操作成功 / 成功 | 成功 |
| `1000` | 请刷新！ | 未登录 / Cookie 过期 |
| `1008` | 系统异常 | 业务异常，常见于**缺必填参数** |
| `1617` | 分页参数不能为空 | 缺 `pageNum`/`pageSize` |
| `9002` | 参数不能为空 | `getTaskDataCount` 缺参数 |
| `1001` | 用户无权限 | 该账号无此权限（如学生调 `getDraftTasks`） |
| `1039` | 任务不存在 | 传入的任务 ID 无效 |

### 1.4 ⚠️ `ifLogin:true` 不等于已登录

```
GET  /api/getDraftTasks -> {"ifLogin":true, "status":false, "code":1008, "message":"系统异常"}
POST /api/getDraftTasks -> {"ifLogin":false,"status":false, "code":1000, "message":"请刷新！"}
```

该路径的 GET 未落在鉴权过滤器之后，直接落到处理器。**带不带 Cookie 都一样**。
所以判定登录态必须用 `status === true`，只看 `ifLogin` 会误判。

---

## 2. `GET /api/getAllTasks` — 任务列表 ★

站点「我的任务」页真实调用的就是这个接口（从页面同源 iframe 的 `performance` 条目读出，非猜测）。

### 2.1 请求

```
GET https://task.yungu.org/api/getAllTasks
```

| 参数 | 必填 | 类型 | 说明 |
|---|---|---|---|
| `inCludeTaskStatus` | **是** | string | 状态筛选，见下表。**注意拼写是 `inClude`**，缺了返回 `code 1008` |
| `pageNum` | **是** | int | 页码，从 1 开始。缺了返回 `code 1617` |
| `pageSize` | **是** | int | 每页条数。站点用 10，实测 50/2000 均可 |
| `courseId` | 否 | int/空串 | 按课程筛选，留空 = 全部 |
| `includeContentLike` | 否 | string | 按标题模糊搜索，留空 = 全部 |
| `sortType` | 否 | int | `2` = 按截止时间排序 |

`inCludeTaskStatus` 语义（实测，服务端筛选）：

| 值 | 含义 | 实测 total |
|---|---|---|
| `0` | **未完成（剩余任务）** | 2 |
| `1` | 全部历史（含逾期未交） | 625 |
| `2` | 已完成 | 805 |

> 该参数**不能为空串**，空串返回 `code 1008 系统异常`。

站点实际请求（原样）：

```
GET /api/getAllTasks?courseId=&includeContentLike=&inCludeTaskStatus=0&pageNum=1&pageSize=10&sortType=2
```

### 2.2 curl 示例

```bash
curl -s -H "Cookie: $COOKIE" -H "Referer: https://task.yungu.org/umiTask" \
  "https://task.yungu.org/api/getAllTasks?courseId=&includeContentLike=&inCludeTaskStatus=0&pageNum=1&pageSize=50&sortType=2"
```

### 2.3 响应

```json
{
  "ifLogin": true, "status": true, "message": "操作成功", "code": 0,
  "content": {
    "pageSize": 50,
    "pageNum": 1,
    "total": 2,
    "data": [
      {
        "count": 1,
        "groupName": "待修改",
        "taskList": [ { /* 任务对象，见 2.4 */ } ]
      },
      {
        "count": 1,
        "groupName": "今天要交",
        "taskList": [ { /* 任务对象 */ } ]
      }
    ]
  }
}
```

**关键结构**：`content.data` **不是平铺的任务数组**，而是「分组」数组；
每个分组有 `groupName`（中文分组名，如 `待修改` / `今天要交` / `list`）和 `taskList`（真正的任务数组）。
所以解析必须**两层展开**，直接遍历 `content.data` 会拿到分组而不是任务（这是个很容易踩的坑）。

| 字段 | 类型 | 说明 |
|---|---|---|
| `content.total` | int | 符合该筛选的任务**总数**（可能是字符串，用 `int()` 兜底） |
| `content.pageNum` / `pageSize` | int | 回显分页参数 |
| `content.data[].count` | int | 该分组任务数 |
| `content.data[].groupName` | string | 分组名 |
| `content.data[].taskList[]` | array | 任务对象 |

### 2.4 任务对象字段（实测全部 49 个）

核心字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `taskPublishId` | int | 发布 ID（**这是查详情用的 ID**） |
| `taskId` | int | 任务 ID |
| `courseId` / `courseName` | int / string | 课程 |
| `title` | string | 任务标题 |
| `taskDescription` | string | 任务说明（**HTML**，需去标签） |
| `deadline` | string | 截止时间（展示用，如 `09-11 22:00`，**不含年份**） |
| `deadlineTimeMillis` | int | 截止时间戳（毫秒）——**要算逾期用这个，别解析 `deadline`** |
| `publishTime` | string | 发布时间（展示用，如 `09-10`） |
| `publishTimeMillis` | int | 发布时间戳（毫秒） |
| `expectFinishTime` | int | 预计用时（分钟） |
| `doTaskStatus` | string | 状态文本，见 §3 |
| `doTaskStatusId` | int | 状态编码，见 §3 |
| `ifTimeout` | bool/**null** | 是否逾期，**三态**，见 §3 |
| `over` | bool | 任务本身是否已结束（结课） |
| `modifiedTime` | string | 最后修改时间（`yyyy-MM-dd HH:mm:ss`） |
| `needEnclosure` | bool | 是否要求附件 |
| `ifPersonalTask` | bool | 是否个人任务 |
| `origin` / `distributionType` | int | 来源 / 分发方式 |

其余字段（多为教师端统计，学生视角常为 `null`）：
`stuId` `teamId` `taskStatus` `taskStatusId` `useTimeMinutes` `totalUseTimeMinutes`
`commitUseTimeCount` `unCommitedStudentCount` `commitStudentCount` `modifyStudentCount`
`finishStudentCount` `taskTotalStudentCount` `groups` `ifIsOpenTaskPublish` `notTimeOutCount`
`message` `createUser` `evaluationItemId` `coverImage` `evaluationStudentCount` `ifTiming`
`taskAttributes` `ifAdjunct` `ifReadAdjunct` `ifComments` `ifReadComments` `ifDoubleRelease`
`ifCutOff` `performance`

---

## 3. 状态：怎么区分「已交 / 待修改 / 逾期」

### 3.1 状态编码（1432 条任务全量枚举，无未知值）

| `doTaskStatusId` | `doTaskStatus` | 含义 |
|---|---|---|
| `1` | 未交 | 没交 |
| `2` | 已确认 | 交了且教师已确认 |
| `3` | 待修改 | 教师退回要求修改 |
| `4` | 已交 | 交了，等教师确认 |

### 3.2 ⚠️「逾期」不是状态，是独立字段

`ifTimeout` 是**三态**字段：`true` / `false` / **`null`**（null 实测有 16 条）。
所以判定必须写 `t.get("ifTimeout") is True`；写成 `if t.get("ifTimeout")` 在 `None` 时虽也是假，
但会掩盖"未知"与"不逾期"的区别，做统计时要留意。

站点 UI 用的是 6 态词表（bundle i18n `homeworkManagement.status.*` 恰好 6 项），
由 `doTaskStatusId` + `ifTimeout` 合成：

| 派生标签 | 条件 | 实测条数 |
|---|---|---|
| 未交 | id=1，不逾期 | 1 |
| 逾期未交 | id=1，`ifTimeout=true` | 234 |
| 准时提交 | id=4，不逾期 | 527 |
| 逾期提交 | id=4，`ifTimeout=true` | 416 |
| 待修改 | id=3 | 1 |
| 教师已确认 | id=2 | 253 |

**两个逾期口径不相等（重要）**：

- 客观字段 `ifTimeout=true` → **709** 条
- 派生标签含「逾期」字样 → **650** 条
- 差的 **59** 条是 `id=2 已确认 + ifTimeout=true`：**已确认的显示优先级高于逾期**

用的时候必须说清是哪个口径，否则两个数对不上。

---

## 4. `GET /api/taskPublish/getTaskCountForStudent` — 任务计数 ★

只要一个数字、不要列表时用这个，比拉列表便宜。

### 4.1 请求

```
GET https://task.yungu.org/api/taskPublish/getTaskCountForStudent?courseId=
```

| 参数 | 必填 | 说明 |
|---|---|---|
| `courseId` | 否 | 留空 = 全部课程 |

### 4.2 响应（实测）

```json
{"ifLogin":true,"status":true,"message":"成功","code":0,"content":{
  "totalCount": 2,        "dueTodayCount": 1,   "dueTomorrowCount": 0,
  "dueRecentlyCount": 0,  "delayedCount": 1,    "allDelayedCount": 1,
  "dueUpdateCount": 1,    "todayCount": 0,      "yesterdayCount": 1,
  "earlierCount": 1,      "otherCount": 0}}
```

| 字段 | 说明 |
|---|---|
| `totalCount` | **剩余任务总数** |
| `dueTodayCount` / `dueTomorrowCount` / `dueRecentlyCount` | 今天 / 明天 / 近期到期 |
| `delayedCount` / `allDelayedCount` | 已逾期 / 逾期合计 |
| `dueUpdateCount` | 待更新 |
| `todayCount` / `yesterdayCount` / `earlierCount` / `otherCount` | 今日新增 / 昨日新增 / 更早 / 其他 |

实测 `totalCount`（2）与 `getAllTasks?inCludeTaskStatus=0` 的 `content.total`（2）**一致** —— 可互为校验。

---

## 5. `POST /api/student/getAchievementDetail` — 任务详情与评论 ★

**教师评论就在这里。** 也是拿 `captureId`（= `taskUserRelationId`）的唯一入口。

### 5.1 请求

```
POST https://task.yungu.org/api/student/getAchievementDetail
Content-Type: application/json

{"taskPublishId": 89939}
```

| 参数 | 必填 | 类型 | 说明 |
|---|---|---|---|
| `taskPublishId` | **是** | int（**必须 JSON body，不能当 query 传**） | 任务发布 ID，来自任务列表的 `taskPublishId` |

> ⚠️ **必须用 POST + body**。把它拼成 query string 用 GET 会返回 `code 1008 系统异常`（实测）。
> 该报错信息不提示原因，容易误判成"没权限"。

### 5.2 响应关键字段（实测）

| 字段 | 类型 | 说明 |
|---|---|---|
| `taskPublishId` | int | 回显任务 ID |
| `taskId` | int | 任务 ID |
| `taskTitle` | string | **任务标题** —— 用它核对评论归属，见 §5.4 |
| `courseId` | int | 课程 ID（注意：本接口**不返回** `courseName`） |
| `taskUserRelationId` | int | **就是 `captureId`**，可传给 `/api/capture/getCaptureByCaptureId` |
| `achievementId` | int | 成果 ID |
| `achievementStatus` | int | 成果状态 |
| `taskStatus` | int | 任务状态 |
| `ifTimeout` | bool | 是否逾期 |
| **`feedback`** | array | **评论列表，见 §5.3** |
| `fileModelList` | array | 我提交的文件（`fileId`/`fileName`/`url`/`downloadUrl`…） |
| `achievementUserResponse` | object | 学生本人信息（`userId`/`userName`/`completeStatus`/`overdueStatus`）—— **`userId` 就是"我"，用来区分评论是谁发的** |
| `finalFeedback` / `aiFeedback` | object|null | 终结性反馈 / AI 反馈（本账号为 `null`） |

### 5.3 `feedback[]` —— 评论（实测字段）

```json
{
  "feedbackId": 319638,
  "parentId": null,
  "userId": <teacher-id>,
  "userName": "<教师姓名>",
  "eName": "<Teacher>",
  "beCommentaryUserId": null,
  "beCommentaryUserName": null,
  "userAvatar": "https://<avatar-or-file-url>",
  "descript": "【待修改】",
  "feedbackTime": "2026-09-16 12:32:58",
  "operation": false,
  "status": 1,
  "awesomeCount": null,
  "currentUserZanId": null,
  "ifZan": false,
  "deletePermission": false,
  "file": []
}
```

| 字段 | 说明 |
|---|---|
| `feedbackId` | 评论 ID（唯一） |
| `descript` | **评论正文**（纯文本，非 HTML） |
| `feedbackTime` | 评论时间（`yyyy-MM-dd HH:mm:ss`） |
| `userId` / `userName` / `eName` | 评论作者 |
| `parentId` | 非空表示这是**某条评论的回复**（指向父评论 `feedbackId`） |
| `beCommentaryUserId` / `beCommentaryUserName` | 被回复/@ 的人 |
| `file[]` | 评论附带的附件 |
| `ifZan` / `awesomeCount` | 是否被点赞 / 点赞数 |

> 该数组**不区分教师和学生**——学生自己的评论也在里面。区分方式见 §5.4。

### 5.4 怎么确定「评论是在哪个任务下发的」

**结论：能有明确归属，而且是接口自己保证的。** 两条依据：

1. **请求即归属**：评论不是全局流，而是**按 `taskPublishId` 取**的。
   所以你请求哪个任务，拿到的就是哪个任务的评论。
2. **响应自带身份，可交叉核对**：同一个响应里同时返回 `taskTitle` / `taskId` / `courseId`，
   可以和任务列表里的标题比对。

实测核对（两个任务分别取，标题完全一致）：

```
列表里的任务: Terminal Advanced        |  详情接口返回: Terminal Advanced        -> 一致: True
   taskPublishId=89939 taskId=701059 courseId=18348 taskUserRelationId=4369061
   评论 9 条（全部来自 <教师姓名>）
列表里的任务: Worksheet and Student ID  |  详情接口返回: Worksheet and Student ID  -> 一致: True
   taskPublishId=90695 taskId=704937 courseId=18348 taskUserRelationId=4401818
   评论 0 条
```

**区分「老师」和「自己」**：用 `feedback[].userId` 与 `achievementUserResponse.userId` 比较 ——
相等就是自己发的，不等就是他人（老师/同学）。实测样例：

```
2026-09-15 14:53:35  <教师姓名>（老师）：Your project must use at least one custom block ...
2026-09-15 10:56:30  <学生姓名>（我）：<评论正文>"是不是老师"只能用 `userId != 我` 近似判断。
> 若要精确到"哪一科的老师"，可再调 `/api/getMixedPublishDetail?taskPublishId=N` 取 `mainTeachers[]` 比对。

### 5.5 解析代码

```python
import json, urllib.request

BASE = "https://task.yungu.org"
COOKIE = open("~/yungu-tasks/cookie.txt").read().strip()


def fetch_comments(task_publish_id, cookie=COOKIE):
    """取某任务的评论。返回 (任务信息, 评论列表)。"""
    req = urllib.request.Request(
        BASE + "/api/student/getAchievementDetail",
        data=json.dumps({"taskPublishId": int(task_publish_id)}).encode("utf-8"),
        headers={"Cookie": cookie, "Content-Type": "application/json;charset=UTF-8",
                 "Referer": BASE + "/umiTask", "X-Requested-With": "XMLHttpRequest"},
        method="POST")
    with urllib.request.urlopen(req, timeout=25) as r:
        env = json.loads(r.read().decode("utf-8"))
    if env.get("status") is not True:
        raise RuntimeError("失败 code=%s message=%s" % (env.get("code"), env.get("message")))
    c = env["content"]
    me = (c.get("achievementUserResponse") or {}).get("userId")
    comments = [{
        "id": f.get("feedbackId"),
        "who": f.get("userName"),
        "is_me": f.get("userId") == me,
        "time": f.get("feedbackTime"),
        "text": f.get("descript"),
        "reply_to": f.get("parentId"),
        "files": [x.get("fileName") for x in (f.get("file") or [])],
    } for f in (c.get("feedback") or [])]
    task = {"taskPublishId": c.get("taskPublishId"), "taskId": c.get("taskId"),
            "title": c.get("taskTitle"), "courseId": c.get("courseId"),
            "captureId": c.get("taskUserRelationId"),
            "my_files": [x.get("fileName") for x in (c.get("fileModelList") or [])]}
    return task, comments


if __name__ == "__main__":
    t, cs = fetch_comments(89939)
    print("任务：%s（taskPublishId=%s, captureId=%s）" % (t["title"], t["taskPublishId"], t["captureId"]))
    for c in cs:
        print("  %s %s%s：%s" % (c["time"], c["who"], "（我）" if c["is_me"] else "（老师）", c["text"]))
```

---

## 6. 其他接口（未深度验证）

### 6.1 `GET /api/getMixedPublishDetail` — 任务详情（作业正文在这里）

```
GET /api/getMixedPublishDetail?taskPublishId=91509
Cookie: <你的会话>
```

**这是唯一能拿到「作业正文」的接口**，与 §5 的 `getAchievementDetail` 分工不同：

| | `getMixedPublishDetail` | `student/getAchievementDetail` |
|---|---|---|
| 方法 | **GET**（query 传 `taskPublishId`） | POST（JSON body） |
| 作业正文 `taskContent` / `taskDescription` | ✅ **HTML** | — |
| 老师的附件 `fileList` | ✅ | — |
| 我的提交 `fileModelList` | — | ✅ |
| 教师评论 `feedback` | — | ✅ |
| 全班名单 `students` | ✅（**含他人隐私**，见下） | — |
| 授课教师 `mainTeachers` / 班级 `groups` | ✅ | — |

实测字段（`content` 29 个，2026-09-22 于 `taskPublishId=91509`）：

| 字段 | 示例 / 说明 |
|---|---|
| `taskTitle` | 任务标题 |
| `taskContent` / `taskDescription` | **作业正文，HTML**（含 `<img src="https://yungu-public.oss…">` 等图片） |
| `courseId` / `courseName` | 课程 |
| `sendTime` / `endTime` | 发布 / 截止时间 |
| `useTime` | 预计用时（分钟） |
| `totalScore` | 分值（字符串，如 `"100"`） |
| `needEnclosure` | 是否要求附件 |
| `evaluationItemId` | 关联的素养评价项 id |
| `taskStatusId` / `doTaskStatusId` / `over` | 任务状态 / 我的完成状态 / 是否已结束 |
| `distributioType` / `ifTiming` / `duty` / `scope` / `auditStatus` | 分发方式等；本样本多为 `null`/`false` |
| `mainTeachers` | 授课教师列表 |
| `groups` | 班级/分组 |
| **`fileList`** | ⚠️ **老师发布的附件**（如「评分标准.pages」）—— **不是**我提交的文件 |
| **`students`** | ⚠️ **全班名单，含他人隐私**，见下 |

> **我提交的文件在 `getAchievementDetail` 的 `fileModelList`**，不在这里。
> 早期版本文档把 `fileList` 注成「我提交的文件」，是错的，已修正。

#### ⚠️ `students` 含第三方隐私 —— 请勿扩散或聚合

实测 `students` 是**整个班级的名单**（本样本 47 人），每人的字段：

```
userId, userName, eName, userAvatar, status, teamId, distributioType,
message, taskUserRelationId, userFileCount, totalCount, file
```

- **能看到的**：全班真实姓名、英文名、头像 URL，以及 `status`（谁交了、谁没交 —— 本样本 42 人未交 / 5 人已交）
- **看不到的**：同学提交的**文件内容**（实测 `file` 对所有同学为空、`userFileCount` 全为 0）
- **仍然敏感**：这已经是他人的个人信息 + 学业状态。**不要导出、不要汇总、不要发布**
- 本仓库的文档与脚本**不收集、不存储**这个字段；示例里也从未打印过任何同学姓名


| 接口 | 实测结果 |
|---|---|
| `GET /api/getTaskList?pageSize=100&pageNum=1` | `status:true, code:0`，`content` 形如 `{ing, beoverdue, complete, taskList:{pageSize,pageNum,total,data}}`。<br>注意它把列表**包在 `taskList` 字段里**，且带 `ing/beoverdue/complete` 三个聚合计数，结构与 `getAllTasks` 不同。`POST` 同样可调。 |
| `GET /api/getTaskDataCount?pageSize=100&pageNum=1` | `code 9002 参数不能为空`，需其它必填参数 |
| `POST /api/getDraftTasks` | `code 1001 用户无权限`（学生账号） |
| `GET /api/getMixedPublishDetail?taskPublishId=91509` | `status:true`，`content` 共 29 个字段。见下方专节。 |

---

## 7. 解析代码（可直接跑）

```python
import json, urllib.request, urllib.parse

BASE = "https://task.yungu.org"
COOKIE = open("~/yungu-tasks/cookie.txt").read().strip()

DO_STATUS_ID = {1: "未交", 2: "已确认", 3: "待修改", 4: "已交"}
DERIVED = {(1, False): "未交", (1, True): "逾期未交",
           (4, False): "准时提交", (4, True): "逾期提交",
           (3, False): "待修改", (3, True): "待修改",
           (2, False): "教师已确认", (2, True): "教师已确认"}


def call(path, params=None):
    """发请求并拆信封，返回 content。失败抛异常（含 code/message，便于定位）。"""
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={
        "Cookie": COOKIE,
        "Accept": "application/json, text/plain, */*",
        "Referer": BASE + "/umiTask",
        "X-Requested-With": "XMLHttpRequest",
    })
    with urllib.request.urlopen(req, timeout=25) as r:
        env = json.loads(r.read().decode("utf-8"))
    if env.get("status") is not True:
        raise RuntimeError("调用失败 code=%s message=%s" % (env.get("code"), env.get("message")))
    return env["content"]


def fetch_tasks(status="0", page_size=50, page_num=1):
    """拉任务并摊平成扁平列表。status: 0=未完成 1=全部 2=已完成"""
    content = call("/api/getAllTasks", {
        "courseId": "", "includeContentLike": "",
        "inCludeTaskStatus": status,
        "pageNum": page_num, "pageSize": page_size, "sortType": 2,
    })
    out = []
    for group in content.get("data") or []:          # 第一层：分组
        for t in group.get("taskList") or []:        # 第二层：任务（必摊平！）
            out.append({
                "group": group.get("groupName"),
                "title": t.get("title"),
                "course": t.get("courseName"),
                "status": DERIVED.get((t.get("doTaskStatusId"), t.get("ifTimeout") is True),
                                      t.get("doTaskStatus") or "-"),
                "status_id": t.get("doTaskStatusId"),
                "overdue": t.get("ifTimeout") is True,
                "deadline": t.get("deadline"),                        # 展示用，无年份
                "deadline_ms": t.get("deadlineTimeMillis"),           # 计算用
                "expect_min": t.get("expectFinishTime"),
                "taskPublishId": t.get("taskPublishId"),
            })
    return out, int(content.get("total") or 0)


if __name__ == "__main__":
    rows, total = fetch_tasks("0")
    print("剩余任务 %d 条（服务端 total=%s）" % (len(rows), total))
    for r in rows:
        print("  [%s] %-40s %-18s %s" % (r["group"], r["title"], r["course"], r["deadline"]))
```

输出：

```
剩余任务 2 条（服务端 total=2）
  [待修改] Terminal Advanced          大学AI建模与算法 I   09-11 22:00
  [今天要交] Worksheet and Student ID  大学AI建模与算法 I   09-16 22:00
```

---

## 8. 坑清单

1. **`content.data` 是分组不是任务** —— 必须两层展开（`data[].taskList[]`），这是最容易踩的。
2. **`inCludeTaskStatus` 拼写**是 `inClude`（大写 L），不是 `include`；且**必填**，空串或缺失都报 `1008`。
3. **`pageNum` / `pageSize` 必填**，否则 `code 1617`。
4. **`deadline` 没有年份**（`09-11 22:00`），跨年比较要用 `deadlineTimeMillis`。
5. **`ifTimeout` 是三态**（`true`/`false`/`null`），别当普通布尔。
6. **`ifLogin:true` 不代表调用成功**，判成功只认 `status === true`。
7. **`taskDescription` 是 HTML**，要展示得先剥标签。
8. **任务状态与筛选档是两回事**：`inCludeTaskStatus` 是服务端筛选（0/1/2），
   `doTaskStatus` 是任务自身状态（1/2/3/4）。想看历史状态分布得用 `--status 1` 或 `2`。
9. **查评论的接口必须 POST + JSON body**，拼成 GET query 会返回 `code 1008 系统异常`（信息很误导）。
10. **`captureId` ≠ `taskPublishId`**：传错会得到 `code 102061 卡片内容不存在`。
    真实 `captureId` = `getAchievementDetail` 返回的 `taskUserRelationId`（如 `4369061`，而 `taskPublishId` 是 `89939`）。
11. **评论数组不区分身份**，学生自己的评论也在 `feedback[]` 里；
    用 `feedback[].userId == achievementUserResponse.userId` 判"是不是我发的"。
