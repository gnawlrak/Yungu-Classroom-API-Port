# 日程 / 课表接口文档（task.yungu.org）

> 覆盖「我的日程」（路由 `https://task.yungu.org/#/calendar`，标题「我的日程」）用到的接口。
> 所有请求/响应样例均为**实测抓取**（你自己的学生账号，2026-09-16），非推测。
> 只读接口。

---

## 0. 关键前提：「日程」是另一个子应用，接口前缀不是 `/api/`

「日程」页本身只是个壳，真正渲染的是**同源子应用**：

```
https://task.yungu.org/newSchoolCalendar/#/index
```

所以它的接口走 **`/calendar/api/...`** 前缀，**不是** `/api/...`。
父应用埋点参数里 `submoduleName` 直接写着「**智能课表**」，可作定位佐证。

站点共有 10 个接口前缀族（这是全量提取的结果）：
`/api/`(主应用) · `/calendar/api/` · `/evaluation/api/` · `/course/api/` · `/iot/api/` ·
`/leave/api/` · `/center/api/` · `/health/api/` · `/message/api/` · `/work/api/` · `/task/api/`

---

## 1. 接口清单

| # | 方法 | 路径 | 用途 | 验证状态 |
|---|---|---|---|---|
| 1 | `GET` | `/calendar/api/personal/schdedule/templateForPc` | **课表**（周视图） | ★ 实测通过 |
| 2 | `GET` | `/calendar/api/current/user` | 当前身份（学生/家长/教师） | ★ 实测通过 |
| 3 | `GET` | `/calendar/api/teaching/allStageGrade` | 学部/年级列表（校历页用） | ◐ 实测有响应 |

> 注意 #1 路径里的 **`schdedule` 是站点自己拼错的**（正常应为 `schedule`）。
> 照抄才能命中，写成 `schedule` 会 404。

---

## 2. 通用约定

与任务接口**完全一致**（同一个统一响应信封），只是路径前缀不同：

```json
{"ifLogin": true, "status": true, "message": "成功", "code": 0, "content": ..., "ifAdmin": false}
```

- 成功判据：`status === true`（`code === 0`）
- 未登录 / 会话过期：`{"ifLogin":false,"status":false,"message":"请刷新！","code":1000,"content":null}`
- 鉴权：同样带浏览器登录后的 Cookie 请求头

```bash
COOKIE="$(cat ~/yungu-tasks/cookie.txt)"
```

---

## 3. `GET /calendar/api/current/user` — 当前身份 ★

检查会话在这个子应用里是否有效、拿到 `userId`。

```bash
curl -s -H "Cookie: $COOKIE" -H "Referer: https://task.yungu.org/newSchoolCalendar/" \
  "https://task.yungu.org/calendar/api/current/user"
```

响应 `content`（实测）：

```json
{
  "name": "<学生姓名>",
  "avatar": "https://<avatar-or-file-url>",
  "userId": <student-id>,
  "identify": ["student"],
  "currentIdentity": "student",
  "identityShowName": "<学生姓名 Student Name>",
  "studentNo": null,
  "stage": 4,
  "campusNum": 3,
  "schoolId": 1,
  "schoolOutPutModel": {"schoolId": 1, "schoolName": "杭州云谷学校", "schoolEnName": "Hangzhou Yungu School", ...}
}
```

| 字段 | 说明 |
|---|---|
| `userId` | 用户 ID（= 任务接口里的 `stuId`） |
| `currentIdentity` | 当前身份：`student` / `parent` / `teacher` —— **影响课表内容** |
| `identify` | 拥有的全部身份数组 |
| `stage` | 学段：`1`=幼儿园 `2`=小学 `3`=初中 `4`=高中（取值对照取自 `/calendar/api/teaching/allStageGrade`） |
| `schoolId` / `schoolOutPutModel` | 学校 |

---

## 4. `GET /calendar/api/personal/schdedule/templateForPc` — 课表 ★

站点「我的日程」页真实调用的就是这个接口（从子应用 iframe 的 `performance` 条目读出，非猜测）。

### 4.1 请求

```
GET https://task.yungu.org/calendar/api/personal/schdedule/templateForPc
```

| 参数 | 必填 | 类型 | 说明 |
|---|---|---|---|
| `weekNumber` | 是 | int | 周序号，从 **1** 开始。站点传当前周序号 |
| `queryStartTime` | 是 | int | 时间窗起点，**毫秒时间戳** |
| `queryEndTime` | 是 | int | 时间窗终点，**毫秒时间戳** |

**时间窗就是「本周一 00:00:00 → 本周日 23:59:59.999」（本地时区）**，实测比对：

| | 值 | 换算 |
|---|---|---|
| 站点实际传的 `queryStartTime` | `1789315200000` | 2026-09-14（周一）00:00:00 |
| 站点实际传的 `queryEndTime` | `1789919999999` | 2026-09-20（周日）23:59:59.999 |

自算窗口与站点传参**完全相等**，所以按下面公式算即可：

```python
import datetime

def week_window(offset=0):
    """返回 (周一日期, 起 ms, 止 ms)。offset: 0=本周 1=下周 -1=上周"""
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(weeks=offset)
    start = int(datetime.datetime.combine(monday, datetime.time(0, 0)).timestamp() * 1000)
    return monday, start, start + 7 * 86400000 - 1
```

站点实际请求（原样）：

```
GET /calendar/api/personal/schdedule/templateForPc?weekNumber=1&queryStartTime=1789315200000&queryEndTime=1789919999999
```

### 4.2 curl 示例

```bash
START=$(python3 -c "import datetime;t=datetime.date.today();m=t-datetime.timedelta(days=t.weekday());print(int(datetime.datetime.combine(m,datetime.time(0,0)).timestamp()*1000))")
END=$((START + 604799999))
curl -s -H "Cookie: $COOKIE" -H "Referer: https://task.yungu.org/newSchoolCalendar/" \
  "https://task.yungu.org/calendar/api/personal/schdedule/templateForPc?weekNumber=1&queryStartTime=$START&queryEndTime=$END"
```

### 4.3 响应结构

```json
{
  "ifLogin": true, "status": true, "message": "成功", "code": 0,
  "content": [
    [ /* 周一：条目数组，21 条 */ ],
    [ /* 周二：20 条 */ ],
    [ /* 周三：21 条 */ ],
    [ /* 周四：20 条 */ ],
    [ /* 周五：15 条 */ ],
    [ /* 周六：0 条，空数组 */ ],
    [ /* 周日：21 条 */ ]
  ]
}
```

**关键结构**：`content` 是**长度 7 的二维数组**，下标 `0..6` 依次对应**周一 → 周日**。
每天是一个条目数组。本周实测共 118 条。

> 解析时不要假设每天都有内容（周六是空数组），矩阵下标 = 星期几（`0`=周一）。

### 4.4 条目字段（实测共 65 个）

#### 核心字段（始终有值）

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | string | **事项名 / 课程名**。⚠️ 课程名在 `name`，不在 `courseName`（后者恒为 null） |
| `eName` | string | 英文名 |
| `startTime` / `endTime` | int | 毫秒时间戳。作息项（如「起床」）两者相等 |
| `courseId` | int/null | **判断是不是课的依据**：有值 = 真实课程；`null` = 作息项 |
| `teachers` | array | 教师列表，见下 |
| `playground` | string | 教室，如 `D421`、`足球场（沙坑）` |
| `playgroundId` | int | 教室 ID |
| `subjectName` / `subjectEname` `subjectId` | string/int | 学科 |
| `courseColor` | string | 课程颜色（`#0054AF`），画课表可直接用 |
| `scheduleType` | int | 排课类型（实测 2 / 3 / 5） |
| `weekDay` | int | 星期几（实测 1..5、7） |
| `courseSort` | int | 当天的课序号 |
| `allDay` | bool | 是否全天 |
| `templateId` / `scheduleResultId` | int | 模板 ID / 排课结果 ID |
| `ifRepeat` `repeatType` `repeatCycle` `repeatIntervals` `repeatEndTime` | | 重复规则 |
| `schoolName` / `schoolEname` | string | 学校 |
| `outsidePlaygroundName` | string | 校外场地（有值时用这个而不是 `playground`） |
| `createTime` | int | 创建时间戳 |

#### `teachers[]` 元素字段

```json
{"userId": <teacher-id>, "userName": "<教师姓名>", "userEname": "<Teacher>",
 "avatarUrl": null, "ifIsNecessary": true, "typeLabel": 1,
 "mobile": null, "email": null, "gradeName": null, ...}
```

| 字段 | 说明 |
|---|---|
| `userName` / `userEname` | 教师中文名 / 英文名 |
| `userId` | 教师 ID |
| `typeLabel` | 观测取值 `1` / `2` / `null`。实测分布：33 门次只有 `1`、40 门次全为 `1`、14 门次 `1+2`、**从无「只有 2」的情况** —— 与「1=主讲、2=辅助」一致，但**官方含义未确认**，本文件不把该推断当事实 |
| `ifIsNecessary` | 是否必要教师 |

#### 恒为 null 的字段（本账号视角）

`courseName` `courseEnglishName` `activeSeatNumber` `departments` `mainTeachers`
`assistantTeachers` `mainTeacherNumber` `assistantTeacherNumber` `students`
`joinStudentGroupList` `joinStudentNumber` `timeType` `joinNumbers` `calendarTagId`
`ifHavePower` `departmentNecessaryModel` `userNecessaryModel` `remark` `createUserId`
`createUserName` `createUserEnglishName` `createUserUnionId` `showCreateButton`
`askOriginal` `repeatGroupId` `repeatString` `customizeType` `ifSyncDingding`
`individualStudents` `recruitActivityId` `recruitActivitySessionId`
`recruitEvaluationActivityId` `attendanceId` `canModifyAddress`
（这些多为教师端/排课端字段，学生接口不返回）

### 4.5 课程 vs 作息项

用 `courseId` 是否为 `null` 区分（实测 118 条中：**57 条课程 / 61 条作息**）：

| 类型 | `courseId` | 例子 |
|---|---|---|
| 真实课程 | 有值（含 `0`） | 大学AI建模与算法 I / 语文 I / 体育 I / 班会 / EL-无限智造3班 |
| 作息项 | `null` | 起床 / 出寝 / 整理 / 体育活动大课间 / 午餐/午休 / 晚餐 / 放学 / 寄宿社区时间 / 个人时间 / 熄灯就寝 |

> 注意 `courseId` 也可能为 `0`（如 `Club试课（体验）`、`十年级晚自修`），
> **不要用 `if courseId:` 判断**（0 是假值会被漏掉），要用 `is not None`。

---

## 5. 解析代码（可直接跑）

```python
import json, urllib.request, urllib.parse, datetime

BASE = "https://task.yungu.org"
COOKIE = open("~/yungu-tasks/cookie.txt").read().strip()
WEEKDAY = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")


def call(path, params=None):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={
        "Cookie": COOKIE,
        "Accept": "application/json, text/plain, */*",
        "Referer": BASE + "/newSchoolCalendar/",
        "X-Requested-With": "XMLHttpRequest",
    })
    with urllib.request.urlopen(req, timeout=25) as r:
        env = json.loads(r.read().decode("utf-8"))
    if env.get("status") is not True:
        raise RuntimeError("调用失败 code=%s message=%s" % (env.get("code"), env.get("message")))
    return env["content"]


def week_window(offset=0):
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(weeks=offset)
    start = int(datetime.datetime.combine(monday, datetime.time(0, 0)).timestamp() * 1000)
    return monday, start, start + 7 * 86400000 - 1


def fetch_timetable(offset=0, include_break=True):
    """返回 [{date, weekday, items:[{start,end,name,course,room,teachers,is_class}]}]"""
    monday, start, end = week_window(offset)
    days = call("/calendar/api/personal/schdedule/templateForPc", {
        "weekNumber": offset + 1, "queryStartTime": start, "queryEndTime": end})
    out = []
    for i, entries in enumerate(days):
        date = monday + datetime.timedelta(days=i)          # 下标就是星期几
        items = []
        for e in entries or []:
            is_class = e.get("courseId") is not None        # 注意用 is not None（courseId 可能是 0）
            if not is_class and not include_break:
                continue
            items.append({
                "start": datetime.datetime.fromtimestamp(e["startTime"] / 1000).strftime("%H:%M"),
                "end": datetime.datetime.fromtimestamp(e["endTime"] / 1000).strftime("%H:%M"),
                "name": e.get("name"),
                "course": e.get("subjectName") if is_class else None,
                "room": e.get("outsidePlaygroundName") or e.get("playground") or "-",
                "teachers": [t.get("userName") for t in (e.get("teachers") or [])],
                "color": e.get("courseColor"),
                "is_class": is_class,
                "is_overdue": False,
            })
        items.sort(key=lambda x: x["start"])
        out.append({"date": date.isoformat(), "weekday": WEEKDAY[date.weekday()], "items": items})
    return out


if __name__ == "__main__":
    for day in fetch_timetable(0, include_break=False):      # 只要课程
        if not day["items"]:
            continue
        print("── %s %s ──" % (day["date"], day["weekday"]))
        for it in day["items"]:
            print("  %s-%s  %-30s %-12s %s" % (
                it["start"], it["end"], it["name"][:28], it["room"][:10], "/".join(it["teachers"])))
```

输出：

```
── 2026-09-14 周一 ──
  08:00-08:40  大学AI建模与算法 I       D416-417   <教师姓名>/<教师姓名>
  08:45-09:25  语文 I                D419       <教师姓名>
  ...
```

---

## 6. 其他接口（未深度验证）

`GET /calendar/api/teaching/allStageGrade` — 校历页用来取学部/年级列表：

```json
{"status":true,"code":0,"content":[
  {"id":1,"stageName":"幼儿园","stageEname":"Kindergarten","stage":1,
   "grades":[{"id":4,"gradeName":"托班","gradeEname":"PreK","grade":-3}, ...]}, ...]}
```

实测 4 个学部（可作为 `stage` 取值的对照表）：

| `stage` | `stageName` | 年级数 |
|---|---|---|
| 1 | 幼儿园 | 4 |
| 2 | 小学 | 6 |
| 3 | 初中 | 3 |
| 4 | 高中 | 4 |

> 校历（`#/schoolcalendar`）页面本身只调了 `current/user` 和 `allStageGrade`，
> 未捕获到独立的校历数据接口（可能走 socket.io 实时通道）。**未确认，不做推测。**

---

## 7. 坑清单

1. **前缀是 `/calendar/api/` 不是 `/api/`** —— 用任务接口的基址拼课表路径一定 404。
2. **`schdedule` 是站点拼错的**（`schedule` 拼法会 404）。
3. **课程名在 `name`，`courseName` 恒为 null** —— 拿 `courseName` 会全是空。
4. **`courseId` 可能是 `0`** —— 判断是否课程要用 `is not None`，不能用真值判断。
5. **`content` 是 7 天的二维数组**，下标 0..6 = 周一..周日；某天可能是空数组。
6. **时间窗是「本周一 00:00:00 → 本周日 23:59:59.999」本地时区**；
   机器时区不是 `Asia/Shanghai` 时（实测该机是 `CST +0800`）算出的窗口会偏，需显式指定日期。
7. **`startTime == endTime` 的条目是时间点**（如「起床」07:00-07:00、`allDay=false`），不是零长度区间。
8. **教室位置优先取 `outsidePlaygroundName`**（校外场地），有值时 `playground` 可能不适用。
