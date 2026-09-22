#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yungu_tasks.py — task.yungu.org 任务/课表/评论读取、接口侦察，以及（可选的）成果提交

读取类操作只访问**你自己账号**的数据；不含任何鉴权绕过。
提交类操作（submit）**默认不发送任何请求**，且需校方授权 —— 详见 docs/api-submit.md。

六个子命令
  tasks     读取并打印「剩余任务」（默认 inCludeTaskStatus=0，即未完成）
  timetable 读取并打印课表（「日程」同源子应用，可指定周）
  comments  读取任务评论（含教师点评），并标明每条评论属于哪个任务
  submit    上传成果文件并提交任务（默认 dry-run；需 --yes 才真的写）
  probe     用你自己的会话探测各候选接口，报告 code / message / 登录态
  recon     枚举站点对外开放的 /api/ 接口（从公开 CDN 的前端 bundle 静态提取）

依赖：Python 3 标准库，无需 pip install。

会话来源（优先级从高到低）
  --cookie "NAME=VALUE; NAME2=VALUE2"
  --cookie-file cookie.txt
  环境变量 YUNGU_COOKIE
  脚本同目录下的 cookie.txt        <- 默认兜底，所以 `python3 yungu_tasks.py tasks` 可零参数直接跑

取 Cookie：浏览器登录 https://task.yungu.org → F12 → Network → 任一 /api/ 请求
          → Headers → Request Headers → 复制 Cookie 整行。

示例
  python3 yungu_tasks.py tasks                       # 读剩余任务（自动用同目录 cookie.txt）
  python3 yungu_tasks.py tasks --verbose             # 带 ID / 发布日 / 预计用时
  python3 yungu_tasks.py tasks --status 1            # 全部历史（含逾期未交）
  python3 yungu_tasks.py tasks --overdue             # 只看逾期（ifTimeout=true）
  python3 yungu_tasks.py tasks --group 待修改         # 按派生状态筛
  python3 yungu_tasks.py tasks --json                # 输出 JSON
  python3 yungu_tasks.py timetable                   # 本周课表
  python3 yungu_tasks.py timetable --week 1          # 下周
  python3 yungu_tasks.py timetable --all             # 连作息项（起床/出寝/整理）一起列
  python3 yungu_tasks.py comments                      # 剩余任务的评论
  python3 yungu_tasks.py comments --teacher-only       # 只看老师/他人发的
  python3 yungu_tasks.py submit --task 91958 --file hw.pdf          # dry-run，不发
  python3 yungu_tasks.py submit --task 91958 --file hw.pdf --yes    # 真的提交（需授权）
  python3 yungu_tasks.py probe                       # 各候选接口返回一览
  python3 yungu_tasks.py recon --bundle-url https://cdn-assets.yungu.org/task/<版本>/index.js

-----------------------------------------------------------------------------
已实测确认的接口契约（2026-09，学生视角）
-----------------------------------------------------------------------------
剩余任务计数：
  GET /api/taskPublish/getTaskCountForStudent?courseId=
  -> content: {todayCount, yesterdayCount, earlierCount, delayedCount,
               dueTodayCount, dueTomorrowCount, dueRecentlyCount, otherCount,
               dueUpdateCount, allDelayedCount, totalCount}

任务列表（站点「我的任务」页真实调用）：
  GET /api/getAllTasks?courseId=&includeContentLike=&inCludeTaskStatus=0
                        &pageNum=1&pageSize=10&sortType=2
  必填：inCludeTaskStatus（缺了会 code 1008「系统异常」）、pageNum、pageSize
  -> content: {pageSize, pageNum, total, data:[{count, groupName, taskList:[...]}]}

  inCludeTaskStatus 实测语义：0=未完成（剩余任务） / 1=全部历史（含逾期未交） / 2=已完成
  任务字段：title, courseName, doTaskStatus(文本), doTaskStatusId(编码),
            deadline, deadlineTimeMillis, publishTime, expectFinishTime,
            taskDescription, ifTimeout, taskPublishId, taskId, courseId, teamId
  已见 doTaskStatusId：1=未交 2=已确认 3=待修改 4=已交
      （全量枚举，1432 条样本无未知值）
  「逾期」不是状态，而是独立字段 ifTimeout（true/false/**null**，注意可能为 null）
  站点 UI 的 6 态标签由两者合成（bundle i18n homeworkManagement.status.*）：
      未交 / 逾期未交 / 待修改 / 逾期提交 / 准时提交 / 教师已确认
  口径差异：ifTimeout=true 共 709 条，而派生标签含「逾期」的只有 650 条 ——
      差的 59 条是「已确认(id=2) + ifTimeout=true」，已确认的显示优先级高于逾期。
      故 --overdue 用客观字段(709)，--group 用 UI 标签(650)。

课表（「日程」= 同源子应用 https://task.yungu.org/newSchoolCalendar/#/index，
      其父应用埋点 submoduleName 就写着「智能课表」）：
  GET /calendar/api/current/user
  GET /calendar/api/personal/schdedule/templateForPc?weekNumber=&queryStartTime=&queryEndTime=
      ^ 路径里的 schdedule 是站点自己的拼写，照抄才命中
  时间窗 = 本周一 00:00:00 → 本周日 23:59:59.999（本地时区，毫秒时间戳）
  -> content: [ 7 天 ][ 条目 ]，条目字段：
       name(课程/事项名) startTime endTime playground(教室) teachers[{userName,userEname}]
       courseId subjectName weekDay scheduleType
     有 courseId 的才是真实课程；起床/出寝/整理 这类是作息项（courseId 为 null）

统一响应信封：{status, code, message, content, ifLogin, ifAdmin}
  code 0=成功 / 1000=未登录（message「请刷新！」）/ 1008=业务异常 / 1009x 参数类错误
  注意：`ifLogin:true` 不能单独作为登录判据 —— GET /api/getDraftTasks 无论是否带
  Cookie 都返回 {ifLogin:true, status:false, code:1008}（该路径未落在鉴权过滤器之后）。
  只有 status:true 才算调用成功。
"""

import argparse
import base64
import datetime
import email.utils
import hashlib
import hmac
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("YUNGU_BASE", "https://task.yungu.org").rstrip("/")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
HERE = os.path.dirname(os.path.abspath(__file__))

NOT_LOGGED_IN_CODES = {1000, 401, 403}
LOGIN_HINTS = ("请刷新", "登录", "未登录", "login", "unauthorized")

COUNT_ENDPOINT = "/api/taskPublish/getTaskCountForStudent"
LIST_ENDPOINT = "/api/getAllTasks"

# 课表：「日程」是同源子应用 newSchoolCalendar（埋点名 = 智能课表）
# 注意接口路径里的 schdedule 是站点自己的拼写，照抄才命中
CAL_USER_ENDPOINT = "/calendar/api/current/user"
TIMETABLE_ENDPOINT = "/calendar/api/personal/schdedule/templateForPc"
DAY_MS = 86400000
WEEKDAY_CN = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")

# inCludeTaskStatus 实测语义
STATUS_MODES = {
    "0": "未完成（剩余任务）",
    "1": "全部历史（含逾期未交）",
    "2": "已完成",
}

# doTaskStatusId 全量枚举结果（1432 条任务样本，见 README §2.5）
DO_STATUS_ID = {1: "未交", 2: "已确认", 3: "待修改", 4: "已交"}

# 站点 UI 用的 6 态词表（bundle i18n: homeworkManagement.status.*）
# 由 doTaskStatus(4 态) + ifTimeout(逾期布尔) 派生 —— 「逾期」不是独立状态，而是独立字段
DERIVED_STATUS = {
    (1, False): "未交",
    (1, True): "逾期未交",
    (4, False): "准时提交",
    (4, True): "逾期提交",
    (3, False): "待修改",
    (3, True): "待修改",
    (2, False): "教师已确认",
    (2, True): "教师已确认",
}


def derive_status(task):
    """合成站点 UI 的 6 态标签：doTaskStatusId 定基础态，ifTimeout 区分准时/逾期。"""
    sid = task.get("doTaskStatusId")
    late = task.get("ifTimeout") is True
    if sid in (1, 2, 3, 4):
        return DERIVED_STATUS[(sid, late)]
    return str(task.get("doTaskStatus") or "-")


def is_overdue(task):
    """逾期 = ifTimeout 为真（注意该字段可能为 None，不能当 False 处理）。"""
    return task.get("ifTimeout") is True

# 计数接口字段 -> 中文
COUNT_LABELS = [
    ("totalCount", "剩余任务总数"), ("dueTodayCount", "今天要交"), ("dueTomorrowCount", "明天到期"),
    ("dueRecentlyCount", "近期到期"), ("delayedCount", "已逾期"), ("allDelayedCount", "逾期合计"),
    ("dueUpdateCount", "待更新"), ("todayCount", "今天新增"), ("yesterdayCount", "昨天新增"),
    ("earlierCount", "更早"), ("otherCount", "其他"),
]

CANDIDATE_ENDPOINTS = [
    LIST_ENDPOINT, "/api/getTaskList", "/api/getDraftTasks",
    "/api/getTaskDataCount", COUNT_ENDPOINT,
]

# 注意保留子应用前缀（/calendar/api/、/evaluation/api/…）。
# 若写成 /api/… 开头，前缀会被吃掉，/calendar/api/x 会被记成 /api/x，
# 既产生幻影、又漏掉真实路径（这是本脚本历史上踩过两次的坑）。
API_RE = re.compile(r"(?:/[A-Za-z][A-Za-z0-9-]*)?/api/[A-Za-z0-9_/.-]+")
BUNDLE_RE = re.compile(r"https?://cdn-assets\.yungu\.org/task/[0-9]+/index\.js")
SCRIPT_RE = re.compile(r"""(?:src|href)=["']([^"']*task/[^"']*index\.js)["']""")


# --------------------------------------------------------------------------- HTTP

def http_request(path, cookie=None, method="GET", body=None, timeout=25):
    """返回 (http_status, text)。HTTP 错误同样返回正文，便于读 JSON 报错。"""
    url = path if path.startswith("http") else BASE + path
    data = None
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": BASE + "/umiTask",
        "X-Requested-With": "XMLHttpRequest",
    }
    if cookie:
        headers["Cookie"] = cookie
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json;charset=UTF-8"
        method = "POST"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, _decode(resp.read(), resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, _decode(e.read(), e.headers)
    except Exception as e:  # noqa: BLE001
        return 0, "<network error: %s>" % e


def _decode(raw, headers):
    enc = None
    try:
        enc = headers.get_content_charset()
    except Exception:  # noqa: BLE001
        pass
    for c in (enc, "utf-8", "gbk", "latin-1"):
        if not c:
            continue
        try:
            return raw.decode(c)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", "replace")


def parse_json(text):
    try:
        return json.loads(text)
    except Exception:  # noqa: BLE001
        m = re.search(r"[\{\[].*[\}\]]", text or "", re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:  # noqa: BLE001
                return None
    return None


def envelope_state(payload):
    """把响应信封翻译成 (已登录?, 说明)。只有 status:true 才算调用成功。"""
    if not isinstance(payload, dict):
        return None, "响应不是 JSON 信封"
    code, msg = payload.get("code"), str(payload.get("message") or "")
    if code in NOT_LOGGED_IN_CODES:
        return False, "未登录 / 会话失效（code=%s, message=%s）" % (code, msg)
    if payload.get("ifLogin") is False and any(h in msg for h in LOGIN_HINTS):
        return False, "未登录 / 会话失效（code=%s, message=%s）" % (code, msg)
    if payload.get("status") is True:
        return True, "成功（code=%s, message=%s）" % (code, msg)
    return None, "调用异常（code=%s, message=%s, ifLogin=%s）" % (
        code, msg, payload.get("ifLogin"))


def call(path, cookie, params=None, method="GET", body=None):
    """发起调用并返回 (envelope, 说明)。"""
    if params and method == "GET":
        path = path + "?" + urllib.parse.urlencode(params)
    st, text = http_request(path, cookie=cookie, method=method, body=body)
    pl = parse_json(text)
    logged, note = envelope_state(pl)
    return pl, note, st, text


def session_required(args):
    if args.cookie:
        return True
    print("!! 需要会话才能读取任务数据。")
    print("   取 Cookie：浏览器登录 %s → F12 → Network → 任一 /api/ 请求" % BASE)
    print("   → Headers → Request Headers → 复制 Cookie 整行，存成 cookie.txt")
    print("   然后：python3 %s tasks --cookie-file cookie.txt" % os.path.basename(__file__))
    return False


# --------------------------------------------------------------------------- tasks

def flatten(content):
    """把 {data:[{groupName, taskList:[...]}]} 摊平成 [(分组, 任务)]。"""
    rows, total = [], content.get("total")
    for g in content.get("data") or []:
        if not isinstance(g, dict):
            continue
        group = g.get("groupName") or "未分组"
        tasks = g.get("taskList")
        if isinstance(tasks, list):
            for t in tasks:
                if isinstance(t, dict):
                    rows.append((group, t))
    return rows, total


def cmd_tasks(args):
    if not session_required(args):
        return 2

    # ---- 1) 剩余任务计数 ----
    counts = None
    pl, note, st, text = call(COUNT_ENDPOINT, args.cookie, params={"courseId": ""})
    if pl and pl.get("status") is True and isinstance(pl.get("content"), dict):
        counts = pl["content"]
    print("== 剩余任务计数  %s ==" % COUNT_ENDPOINT)
    if counts:
        for k, label in COUNT_LABELS:
            if counts.get(k):
                print("   %-10s %s" % (label, counts[k]))
    else:
        print("   (未取到：%s)" % note)

    # ---- 2) 任务列表 ----
    status = args.status
    params = {
        "courseId": "", "includeContentLike": "",
        "inCludeTaskStatus": status, "pageNum": "1",
        "pageSize": str(args.page_size), "sortType": "2",
    }
    pl, note, st, text = call(LIST_ENDPOINT, args.cookie, params=params)
    if args.dump:
        with open(args.dump, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("\n原始响应已写入 %s" % args.dump)

    if not (pl and pl.get("status") is True and isinstance(pl.get("content"), dict)):
        print("\n!! 任务列表调用失败：%s" % note)
        if "未登录" in note:
            print("   Cookie 可能已过期（有效期约 1-2 周），请重新复制。")
        else:
            print("   用 `probe --cookie-file cookie.txt` 看各接口返回，"
                  "或用 `--endpoint /api/xxx` 指定接口。")
        return 2

    rows, total = flatten(pl["content"])
    mode = STATUS_MODES.get(status, status)
    print("\n== 任务列表  %s ==" % LIST_ENDPOINT)
    print("   筛选 inCludeTaskStatus=%s（%s）  服务端 total=%s  本次取回 %d 条"
          % (status, mode, total, len(rows)))

    if not rows:
        print("\n   该筛选下没有任务。")
        return 0

    cur_group = None
    shown = 0
    summary = {}
    for group, t in rows:
        label = derive_status(t)
        summary[label] = summary.get(label, 0) + 1
        if args.overdue and not is_overdue(t):
            continue
        if args.group != label:            # --group 精确匹配派生状态
            if args.group:
                continue
        shown += 1
        if group != cur_group:
            cur_group = group
            if shown > 1:
                print()
            print("   ── %s ──" % group)
        late = "  [逾期]" if is_overdue(t) else ""
        print("   %-40s %-20s %-8s 截止 %s%s"
              % (str(t.get("title") or "(无标题)")[:38],
                 str(t.get("courseName") or "-")[:18],
                 label[:8], t.get("deadline") or "-", late))
        if args.verbose:
            print("       doTaskStatusId=%s ifTimeout=%s over=%s | taskPublishId=%s courseId=%s 发布=%s"
                  % (t.get("doTaskStatusId"), t.get("ifTimeout"), t.get("over"),
                     t.get("taskPublishId"), t.get("courseId"), t.get("publishTime")))

    print("\n   显示 %d / %d 条" % (shown, len(rows)))
    if not args.group and not args.overdue:
        print("   状态分布：%s" % "  ".join(
            "%s=%d" % (k, v) for k, v in sorted(summary.items(), key=lambda x: -x[1])))
        print("   （doTaskStatusId: 1=未交 2=已确认 3=待修改 4=已交；"
              "ifTimeout 为真即逾期 → 派生为「逾期未交/逾期提交」）")

    if args.json:
        print("\n== JSON ==")
        print(json.dumps([{"group": g, "task": t, "derivedStatus": derive_status(t),
                           "overdue": is_overdue(t)} for g, t in rows],
                         ensure_ascii=False, indent=2))
    return 0


# --------------------------------------------------------------------------- timetable

def week_window(offset=0, date_str=None):
    """返回 (周一日期, 起 ms, 止 ms)。

    实测应用的窗口就是「本周一 00:00:00 → 本周日 23:59:59.999」（本地时区），
    例如 weekNumber=1 时它传的 queryStartTime=1789315200000 / queryEndTime=1789919999999
    正好是 2026-09-14(周一) ~ 2026-09-20(周日)。
    """
    if date_str:
        base = datetime.date.fromisoformat(date_str)
    else:
        base = datetime.date.today()
    monday = base - datetime.timedelta(days=base.weekday()) + datetime.timedelta(weeks=offset)
    start = int(datetime.datetime.combine(monday, datetime.time(0, 0)).timestamp() * 1000)
    return monday, start, start + 7 * DAY_MS - 1


def fmt_hm(ms):
    if not ms:
        return "--:--"
    return datetime.datetime.fromtimestamp(ms / 1000).strftime("%H:%M")


def teacher_names(entry):
    out = []
    for key in ("teachers", "mainTeachers", "assistantTeachers"):
        v = entry.get(key)
        if isinstance(v, list):
            for t in v:
                if isinstance(t, dict):
                    n = t.get("userName") or t.get("name") or t.get("userEname")
                    if n and n not in out:
                        out.append(n)
    return out


def cmd_timetable(args):
    if not session_required(args):
        return 2

    # 子应用里的身份（顺带确认会话在这个子应用也有效）
    pl, note, st, _ = call(CAL_USER_ENDPOINT, args.cookie)
    if pl and pl.get("status") is True and isinstance(pl.get("content"), dict):
        c = pl["content"]
        print("身份：%s（%s）" % (c.get("identityShowName") or c.get("name") or "?",
                                 c.get("currentIdentity") or "?"))

    monday, start, end = week_window(args.week, args.date)
    params = {"weekNumber": str(args.week + 1), "queryStartTime": str(start),
              "queryEndTime": str(end)}
    pl, note, st, text = call(TIMETABLE_ENDPOINT, args.cookie, params=params)
    if args.dump:
        with open(args.dump, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("原始响应已写入 %s" % args.dump)

    if not (pl and pl.get("status") is True and isinstance(pl.get("content"), list)):
        print("!! 课表调用失败：%s" % note)
        if "未登录" in note:
            print("   Cookie 可能已过期，请重新取样。")
        return 2

    days = pl["content"]
    print("== 课表  %s ~ %s（共 %d 天）==" % (
        monday.isoformat(), (monday + datetime.timedelta(days=6)).isoformat(), len(days)))
    print("   %s  weekNumber=%s  window=%s..%s" % (TIMETABLE_ENDPOINT, params["weekNumber"], start, end))

    kept = 0
    payload = []
    for i, day in enumerate(days):
        if not isinstance(day, list):
            continue
        date = monday + datetime.timedelta(days=i)
        rows = [e for e in day if isinstance(e, dict)]
        if not args.all:
            # 默认只保留真实课程（有 courseId）；排除 起床/出寝/整理 这类作息项
            rows = [e for e in rows if e.get("courseId")]
        rows.sort(key=lambda e: e.get("startTime") or 0)
        if not rows:
            continue
        print("\n   ── %s %s ──" % (date.isoformat(), WEEKDAY_CN[date.weekday()]))
        for e in rows:
            kept += 1
            t = teacher_names(e)
            print("   %s-%s  %-30s %-14s %s%s" % (
                fmt_hm(e.get("startTime")), fmt_hm(e.get("endTime")),
                str(e.get("name") or e.get("courseName") or "?")[:28],
                str(e.get("playground") or "-")[:12],
                "/".join(t) if t else "-",
                "  [%s]" % e["subjectName"] if e.get("subjectName") and args.verbose else ""))
            if args.verbose:
                print("        courseId=%s scheduleType=%s weekDay=%s" % (
                    e.get("courseId"), e.get("scheduleType"), e.get("weekDay")))
        payload.append({"date": date.isoformat(), "weekday": WEEKDAY_CN[date.weekday()], "items": rows})

    print("\n   共 %d 节%s" % (kept, "" if args.all else "（默认只列课程，加 --all 含作息项）"))
    if args.json:
        print("\n== JSON ==")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


# --------------------------------------------------------------------------- comments

# 任务详情（含评论）。注意：GET 会返回 1008，**必须 POST + body**
ACHIEVEMENT_ENDPOINT = "/api/student/getAchievementDetail"


def fetch_achievement(cookie, task_publish_id):
    """取某任务的成果详情（含 comments）。返回 (content, 错误说明)。"""
    pl, note, st, text = call(ACHIEVEMENT_ENDPOINT, cookie,
                              method="POST", body={"taskPublishId": int(task_publish_id)})
    if not (pl and pl.get("status") is True and isinstance(pl.get("content"), dict)):
        return None, note
    return pl["content"], None


def cmd_comments(args):
    """列出评论，并标明每条评论属于哪个任务（按 taskPublishId 取，响应自带 taskTitle 可核对）。"""
    if not session_required(args):
        return 2

    if args.task:
        targets = [(None, {"taskPublishId": int(x.strip()), "title": "(指定任务)",
                           "deadline": "-"}) for x in str(args.task).split(",") if x.strip()]
        print("== 指定任务 %d 个 ==\n" % len(targets))
    else:
        params = {"courseId": "", "includeContentLike": "", "inCludeTaskStatus": args.status,
                  "pageNum": "1", "pageSize": str(args.limit), "sortType": "2"}
        pl, note, st, text = call(LIST_ENDPOINT, args.cookie, params=params)
        if not (pl and pl.get("status") is True and isinstance(pl.get("content"), dict)):
            print("!! 取任务列表失败：%s" % note)
            return 2
        targets, total = flatten(pl["content"])
        print("== 扫描任务 inCludeTaskStatus=%s：%d 个（服务端 total=%s，--limit 可控）==\n"
              % (args.status, len(targets), total))

    me, n_tasks, n_comments = None, 0, 0
    payload = []
    requests_made = 0
    for group, t in targets:
        # 限流：每个任务一次请求，达到上限即停（对应 README 免责声明第 6 条）
        if requests_made >= args.max_requests:
            print("\n!! 已达请求上限 %d（--max-requests 可调），停止扫描。" % args.max_requests)
            break
        if requests_made and args.sleep:
            time.sleep(args.sleep)
        requests_made += 1
        tpid = t.get("taskPublishId")
        c, err = fetch_achievement(args.cookie, tpid)
        if err:
            print("  !! taskPublishId=%s 取详情失败：%s" % (tpid, err))
            continue
        if me is None:
            me = (c.get("achievementUserResponse") or {}).get("userId")
        fb = c.get("feedback") or []
        if args.teacher_only:
            fb = [f for f in fb if f.get("userId") != me]
        if not fb and not args.show_empty:
            continue

        n_tasks += 1
        title = c.get("taskTitle") or t.get("title") or "(无标题)"
        course = t.get("courseName") or "-"
        print("── %s" % title)
        print("   taskPublishId=%s  taskId=%s  courseId=%s  课程=%s  截止=%s%s"
              % (c.get("taskPublishId"), c.get("taskId"), c.get("courseId"), course,
                 t.get("deadline") or c.get("endTime") or "-",
                 "  [逾期]" if c.get("ifTimeout") else ""))
        if not fb:
            print("   （无评论）\n")
        for f in fb:
            n_comments += 1
            mine = f.get("userId") == me
            print("   %s  %s%s：%s" % (f.get("feedbackTime"),
                                      f.get("userName") or "?",
                                      "（我）" if mine else "（老师）",
                                      str(f.get("descript") or "").replace("\n", " ")))
            for fl in (f.get("file") or []):
                print("        [附件] %s" % (fl.get("fileName") or fl.get("url")))
            if f.get("parentId"):
                print("        [回复 parentId=%s]" % f.get("parentId"))
        print()
        payload.append({"task": {"taskPublishId": c.get("taskPublishId"), "taskId": c.get("taskId"),
                                 "title": title, "course": course, "deadline": t.get("deadline"),
                                 "ifTimeout": c.get("ifTimeout")},
                        "comments": fb})

    print("合计：%d 个任务有评论，共 %d 条%s"
          % (n_tasks, n_comments, "（已过滤掉自己发的）" if args.teacher_only else ""))
    if args.json:
        print("\n== JSON ==")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


# --------------------------------------------------------------------------- submit
# 下面三个端点与全部字段，来自 2026-09-22 在**教师专门创建的测试任务**上的实测抓包
# （上传→提交→回读全链路验证：achievementStatus 1 → 4）。
# 不是从接口名推测的 —— 推测会选 /api/capture/submitCapture，那是教师端发布任务用的。
UPLOAD_ENDPOINT = "/api/upload_file/new"
SUBMIT_ENDPOINT = "/api/submitAchievementSendMessage"
OSS_BUCKET = "yungu-common"
# achievementStatus 实测取值：1=未交 3=待修改 4=已交 2=教师已确认
SUBMITTABLE = (1, 3)


def _oss_credentials(cookie):
    """取 OSS 直传凭证。返回 (dict, 错误说明)。"""
    pl, note, st, text = call("/api/sts/token", cookie, params={"type": "1"})
    if isinstance(pl, dict) and pl.get("status") is True and isinstance(pl.get("content"), dict):
        return pl["content"], None
    return None, note


def _oss_put(oss, key, data, mime, timeout=90):
    """把字节直传 OSS（阿里云 V1 签名，HMAC-SHA1，纯标准库）。返回 (状态码, ETag, 错误)。"""
    endpoint = oss["endpoint"].replace("https://", "").replace("http://", "").strip("/")
    url = "https://%s.%s/%s" % (oss["bucketName"], endpoint, key)
    date = email.utils.formatdate(usegmt=True)
    md5 = base64.b64encode(hashlib.md5(data).digest()).decode()
    canon_headers = "x-oss-security-token:%s\n" % oss["stsToken"]
    canon_resource = "/%s/%s" % (oss["bucketName"], key)
    to_sign = "PUT\n%s\n%s\n%s\n%s%s" % (md5, mime, date, canon_headers, canon_resource)
    sig = base64.b64encode(hmac.new(oss["accessSecret"].encode("utf-8"),
                                    to_sign.encode("utf-8"), hashlib.sha1).digest()).decode()
    req = urllib.request.Request(url, data=data, method="PUT", headers={
        "Date": date, "Content-MD5": md5, "Content-Type": mime,
        "x-oss-security-token": oss["stsToken"],
        "Authorization": "OSS %s:%s" % (oss["accessKeyId"], sig),
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.headers.get("ETag"), None
    except urllib.error.HTTPError as e:
        return e.code, None, e.read().decode("utf-8", "replace")[:200]
    except Exception as e:  # noqa: BLE001
        return 0, None, str(e)


def verify_file_readable(cookie, file_id, expect=None):
    """回读该 fileId 的字节 —— 这是判断上传真假的唯一可信判据。

    /api/upload_file/new 只要元数据格式对就会返回 status:true 和 fileId，
    即使字节从没传上去（实测踩过：POST 一发就走，拿到 fileId，回读 404）。
    """
    req = urllib.request.Request(
        "%s/api/preview_file?id=%s" % (BASE, file_id),
        headers={"User-Agent": UA, "Cookie": cookie,
                 "Referer": BASE + "/umiTask", "X-Requested-With": "XMLHttpRequest"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
            if expect is not None and body != expect:
                return False, "回读内容与本地文件不一致（%d vs %d 字节）" % (len(body), len(expect))
            return True, "回读 %d 字节，与本地一致" % len(body)
    except urllib.error.HTTPError as e:
        return False, "回读失败 HTTP %s（字节没真正落到 OSS）" % e.code
    except Exception as e:  # noqa: BLE001
        return False, "回读异常 %s" % e


def upload_file(path, cookie, verify=True):
    """上传一个成果文件，返回 (fileId, 说明)。

    真实流程（2026-09-22 抓包确认，三步，缺一不可）：
      1) GET  /api/sts/token?type=1         拿 OSS 直传凭证
      2) PUT  https://<bucket>.<endpoint>/taskFile/<ts>_<name>   字节直传 OSS
      3) GET  /api/upload_file/new?<元数据>  注册元数据 -> fileId
    注意第 3 步是 GET（静态目录里本来就是 GET，曾被我误改成 POST）。
    """
    name = os.path.basename(path)
    with open(path, "rb") as fh:
        data = fh.read()
    mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
    oss, err = _oss_credentials(cookie)
    if not oss:
        return None, "取 OSS 凭证失败：%s" % err
    key = "%s%d_%s" % (oss.get("ossPath") or "taskFile/", int(time.time() * 1000), name)
    st, etag, oerr = _oss_put(oss, key, data, mime)
    if st != 200:
        return None, "OSS 直传失败 HTTP %s %s" % (st, oerr)
    params = {"fileName": name, "bucketName": oss["bucketName"], "fileSize": str(len(data)),
              "fileType": mime, "fileUrl": key,
              "percent": "100", "uuid": key.split("/")[-1].split("_")[0]}
    pl, note, _, text = call(UPLOAD_ENDPOINT, cookie, params=params)
    fid = None
    if isinstance(pl, dict) and pl.get("status") is True and isinstance(pl.get("content"), dict):
        fid = pl["content"].get("fileId")
    if not fid:
        return None, "注册元数据失败：%s" % note
    msg = "fileId=%s (OSS %dB, ETag=%s)" % (fid, len(data), (etag or "").strip('"')[:12])
    if verify:
        ok, why = verify_file_readable(cookie, fid, data)
        if not ok:
            return None, "上传未真正生效 —— %s" % why
        msg += "；" + why
    return fid, msg


def cmd_submit(args):
    """提交任务成果。默认 dry-run 只打印请求，必须 --yes 才真的写。"""
    if not session_required(args):
        return 2
    if not args.task:
        print("!! 必须指定 --task <taskPublishId>")
        return 2
    args.task = int(str(args.task).split(",")[0].strip())
    if not args.file and not args.text:
        print("!! 至少要给 --file 或 --text")
        return 2
    if not args.yes:
        print("== dry-run（未发送任何请求；确认无误后加 --yes）==\n")

    c, err = fetch_achievement(args.cookie, args.task)
    if not c:
        print("!! 读任务现状失败：%s" % err)
        return 2
    me = (c.get("achievementUserResponse") or {}).get("userId")
    st_now = c.get("achievementStatus")
    print("任务：%s  (taskPublishId=%s)" % (c.get("taskTitle"), c.get("taskPublishId")))
    print("  courseId=%s  taskUserRelationId=%s  当前 achievementStatus=%s  要求附件=%s"
          % (c.get("courseId"), c.get("taskUserRelationId"), st_now, c.get("needEnclosure")))
    if st_now not in SUBMITTABLE:
        print("\n!! 当前状态 %s 不可提交（已交或教师已确认）。" % st_now)
        print("   重交需教师「退回修改」把状态打回 3。脚本不会替你绕过这个限制。")
        return 2
    if c.get("needEnclosure") and not args.file:
        print("\n!! 该任务要求附件（needEnclosure=true），但没给 --file。")
        return 2
    # 先校验身份字段齐全，再决定要不要上传 —— 否则会先在学校存储里留下孤儿文件
    missing = [k for k, v in (("courseId", c.get("courseId")),
                              ("taskPublishId", c.get("taskPublishId")),
                              ("taskUserRelationId", c.get("taskUserRelationId")),
                              ("studentId(我的 userId)", me)) if v is None]
    if missing:
        print("\n!! 现状响应缺少 %s，拒绝继续（尚未上传任何文件）。" % ", ".join(missing))
        print("   可能站点改版。用 `probe --endpoint /api/student/getAchievementDetail` 核对结构。")
        return 2

    file_ids = []
    for p in args.file or []:
        if not args.yes:
            print("  [dry-run] 将上传 %s → OSS 直传（sts/token → PUT OSS → upload_file/new）" % p)
            file_ids.append("<fileId>")
            continue
        fid, msg = upload_file(p, args.cookie)
        print("  %s : %s" % (p, msg))
        if not fid:
            return 2
        file_ids.append(fid)
        time.sleep(args.sleep)
    existing = [f.get("fileId") for f in (c.get("fileModelList") or []) if f.get("fileId")]
    payload_files = file_ids if args.only_new else list(dict.fromkeys(existing + file_ids))

    payload = {"courseId": c.get("courseId"), "fileList": payload_files,
               "studentIds": [me], "teamList": None,
               "taskPublishId": c.get("taskPublishId"),
               "taskUserRelationId": c.get("taskUserRelationId"),
               "textStatus": args.text_status}
    # 必填字段缺任何一个都不发 —— 残缺 payload 会被服务端当成正常请求处理
    missing = [k for k in ("courseId", "taskPublishId", "taskUserRelationId")
               if payload.get(k) is None] + (["studentIds"] if not me else [])
    if missing:
        print("\n!! 现状响应缺少必填字段 %s，拒绝提交（不发送残缺 payload）。" % ", ".join(missing))
        print("   可能站点改版。用 `probe --endpoint /api/student/getAchievementDetail` 核对结构。")
        return 2
    print("\n将发送：POST %s" % SUBMIT_ENDPOINT)
    print("  " + json.dumps(payload, ensure_ascii=False))
    if args.only_new:
        print("  （--only-new：不带之前已上传的附件 %s）" % (existing or "无"))
    if args.text:
        print("  注意：--text 暂不参与提交。纯文字提交的 textStatus 取值未实测，不做猜测。")
    if not args.yes:
        print("\n[dry-run] 未发送。加 --yes 才会真的提交；提交后学生侧无法自助撤回。")
        return 0

    if not args.skip_confirm:
        print("\n⚠️  学生侧没有自助撤回接口，提交后只能请教师「退回修改」。")
        if input("   确认提交？输入 yes 继续：").strip().lower() != "yes":
            print("   已取消，未发送任何请求。")
            return 0

    pl, note, st, text = call(SUBMIT_ENDPOINT, args.cookie, method="POST", body=payload)
    print("\n提交响应：%s" % note)
    time.sleep(args.sleep)
    c2, err2 = fetch_achievement(args.cookie, args.task)
    if c2:
        print("回读校验：achievementStatus %s → %s  附件数 %d  achievementId=%s"
              % (st_now, c2.get("achievementStatus"), len(c2.get("fileModelList") or []),
                 c2.get("achievementId")))
        if c2.get("achievementStatus") in (2, 4):
            print("✅ 提交成功")
            return 0
        print("❌ 状态未变化（%s）" % (err2 or "回读正常但状态没动"))
        return 2
    print("❌ 回读失败：%s" % err2)
    return 2


# --------------------------------------------------------------------------- probe

def cmd_probe(args):
    if not session_required(args):
        return 2
    print("%-46s %-6s %s" % ("endpoint", "HTTP", "结果"))
    print("-" * 112)
    for ep in (args.endpoint and [args.endpoint] or CANDIDATE_ENDPOINTS):
        if ep == LIST_ENDPOINT:
            params = {"courseId": "", "includeContentLike": "",
                      "inCludeTaskStatus": "0", "pageNum": "1", "pageSize": "5", "sortType": "2"}
            pl, note, st, _ = call(ep, args.cookie, params=params)
        elif ep == COUNT_ENDPOINT:
            pl, note, st, _ = call(ep, args.cookie, params={"courseId": ""})
        else:
            pl, note, st, _ = call(ep, args.cookie, method="POST", body={})
        extra = ""
        if isinstance(pl, dict):
            c = pl.get("content")
            if isinstance(c, dict):
                extra = "  content{%s}" % ", ".join(list(c)[:6])
            elif isinstance(c, list):
                extra = "  content[%d]" % len(c)
        print("%-46s %-6s %s%s" % (ep, st, note, extra))
    return 0


# --------------------------------------------------------------------------- recon

def derive_bundle_url(cookie):
    """带会话访问入口页，解析出前端 bundle 地址（未登录时站点会 302 到 CAS）。"""
    for entry in ("/umiTask", "/"):
        st, text = http_request(entry, cookie=cookie)
        for m in BUNDLE_RE.finditer(text or ""):
            return m.group(0)
        for m in SCRIPT_RE.finditer(text or ""):
            return urllib.parse.urljoin(BASE + "/", m.group(1))
    return None


def cmd_recon(args):
    print("== 站点形态 ==")
    st, text = http_request("/api/")
    logged, note = envelope_state(parse_json(text))
    print("   GET /api/  HTTP %s  ->  %s" % (st, text[:180]))
    print("   判定：%s" % note)
    print("   注意：鉴权在路由之前 —— 不存在的接口与真实接口返回同一个信封，"
          "未登录时无法靠探测枚举，只能读前端 bundle。")

    bundle_url = args.bundle_url or derive_bundle_url(args.cookie)
    if not bundle_url:
        print("\n!! 未拿到 bundle 地址（无会话时入口页 302 到 CAS 登录中心）。")
        print("   1) 带会话：python3 %s recon --cookie-file cookie.txt" % os.path.basename(__file__))
        print("   2) 手动指定：F12 → Network → 找 cdn-assets.yungu.org/task/<版本>/index.js")
        print("      再跑：python3 %s recon --bundle-url <那个地址>" % os.path.basename(__file__))
        return 1

    print("\n== 前端 bundle ==\n   %s" % bundle_url)
    st, main = http_request(bundle_url, cookie=args.cookie)
    if st != 200 or not main:
        print("   !! 下载失败 HTTP %s" % st)
        return 1
    root = bundle_url.rsplit("/", 1)[0]
    # chunk 清单有两个来源，都要用：
    #   ① 主包里被点名引用的 <id>.async.js
    #   ② webpack 的声明表 o.e=function(e){...0!==r[e]&&{0:1,1:1,...}}
    #      —— 只靠 ① 会漏掉大量未按名引用的 chunk（实测 340 vs 716 个文件）
    ids = {int(x) for x in re.findall(r"\b(\d{1,4})\.async\.js\b", main)}
    m = re.search(r"0!==r\[e\]&&\{([0-9:,]+)\}", main)
    if m:
        ids |= {int(x) for x in re.findall(r"(\d+):", m.group(1))}
    if not ids:
        ids = set(range(1, 341))
    texts = [main]
    for cid in sorted(ids):
        s, t = http_request("%s/%d.async.js" % (root, cid), cookie=args.cookie)
        if s == 200 and t:
            texts.append(t)
    eps = set()
    for t in texts:
        for m in API_RE.findall(t):
            e = m.rstrip(".,;")
            # 判据是「/api/ 后还有内容」，不能数斜杠 —— 否则会漏掉
            # /api/saveCommentary 这类单段接口（实测漏 9 个）
            if re.search(r"/api/.", e) and not e.rstrip("/").endswith("/api"):
                eps.add(e)
    task_eps = sorted(e for e in eps if re.search(r"task|homework|draft|capture", e, re.I))
    print("   下载 %d 个文件，枚举到 %d 个 /api/ 接口（任务相关 %d）"
          % (len(texts), len(eps), len(task_eps)))
    out = os.path.join(HERE, "yungu_endpoints_discovered.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"bundle": bundle_url, "count": len(eps),
                   "endpoints": sorted(eps), "task_related": task_eps},
                  fh, ensure_ascii=False, indent=2)
    print("   已写入 %s" % out)
    return 0


# --------------------------------------------------------------------------- main

def resolve_cookie(args):
    """会话优先级：--cookie > --cookie-file > YUNGU_COOKIE > 脚本同目录的 cookie.txt。"""
    if args.cookie:
        return args.cookie.strip()
    if args.cookie_file:
        try:
            with open(args.cookie_file, encoding="utf-8") as fh:
                return fh.read().strip()
        except OSError as e:
            print("读取 cookie 文件失败：%s" % e, file=sys.stderr)
            sys.exit(2)
    env = (os.environ.get("YUNGU_COOKIE") or "").strip()
    if env:
        return env
    # 默认兜底：脚本自己所在目录下的 cookie.txt —— 免去每次传 --cookie-file
    beside = os.path.join(HERE, "cookie.txt")
    if os.path.exists(beside):
        try:
            with open(beside, encoding="utf-8") as fh:
                val = fh.read().strip()
            if val:
                return val
        except OSError:
            pass
    return None


def main():
    ap = argparse.ArgumentParser(description="task.yungu.org 剩余任务 / 课表读取与接口侦察")
    ap.add_argument("command", choices=["tasks", "timetable", "comments", "submit", "probe", "recon"])
    ap.add_argument("--cookie", help="Cookie 请求头，原样粘贴")
    ap.add_argument("--cookie-file", help="存放 Cookie 请求头的文件")
    ap.add_argument("--status", default="0",
                    help="tasks 用 inCludeTaskStatus：0=未完成(默认) 1=全部历史 2=已完成")
    ap.add_argument("--page-size", type=int, default=50)
    ap.add_argument("--overdue", action="store_true",
                    help="tasks 用：只列出逾期任务（ifTimeout=true）")
    ap.add_argument("--task", help="comments/submit 用：taskPublishId（comments 可逗号分隔；submit 只取第一个）")
    ap.add_argument("--file", action="append",
                    help="submit 用：要上传的成果文件，可重复")
    ap.add_argument("--text", help="submit 用：预留的文字成果（当前仅记录，不参与提交）")
    ap.add_argument("--only-new", action="store_true",
                    help="submit 用：不带之前已上传但未提交的附件（默认会合并，与应用行为一致）")
    ap.add_argument("--text-status", type=int, default=0,
                    help="submit 用：textStatus，实测有附件提交时为 0")
    ap.add_argument("--yes", action="store_true",
                    help="submit 用：真的发送（缺省只 dry-run 打印请求）")
    ap.add_argument("--skip-confirm", action="store_true",
                    help="submit 用：跳过交互式二次确认（配合 --yes；不建议）")
    ap.add_argument("--teacher-only", action="store_true",
                    help="comments 用：过滤掉自己发的，只看老师/他人评论")
    ap.add_argument("--show-empty", action="store_true",
                    help="comments 用：连没有评论的任务也列出来")
    ap.add_argument("--limit", type=int, default=20,
                    help="comments 用：最多扫描多少个任务（默认 20，每个任务一次请求）")
    ap.add_argument("--max-requests", type=int, default=300,
                    help="comments 用：单次运行的请求数硬上限（默认 300，保护站点）")
    ap.add_argument("--sleep", type=float, default=0.3,
                    help="comments 用：两次请求之间的间隔秒数（默认 0.3）")
    ap.add_argument("--group", help="tasks 用：只看某个派生状态，如 逾期未交/待修改/准时提交/教师已确认")
    ap.add_argument("--week", type=int, default=0,
                    help="timetable 用：0=本周(默认) 1=下周 -1=上周")
    ap.add_argument("--date", help="timetable 用：取该日期所在周，格式 YYYY-MM-DD")
    ap.add_argument("--all", action="store_true",
                    help="timetable 用：连作息项（起床/出寝/整理…）一起列")
    ap.add_argument("--endpoint", help="probe 用：只探这一个接口")
    ap.add_argument("--bundle-url", help="recon 用：前端 bundle 地址")
    ap.add_argument("--dump", help="把原始响应写到该文件")
    ap.add_argument("--json", action="store_true", help="额外打印 JSON")
    ap.add_argument("--verbose", action="store_true", help="打印更多字段")
    args = ap.parse_args()
    args.cookie = resolve_cookie(args)
    return {"tasks": cmd_tasks, "timetable": cmd_timetable, "comments": cmd_comments,
            "submit": cmd_submit, "probe": cmd_probe, "recon": cmd_recon}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
