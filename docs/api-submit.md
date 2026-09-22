# 提交任务成果 —— 接口契约

> **本文所有字段都来自实测抓包，不是从接口名推测的。**
> 验证方式：教师在测试环境专门发布了一条测试任务（`test homework`），
> 在其上完成「上传 → 提交 → 回读」全链路，`achievementStatus` 从 `1` 变为 `4`。
> 抓取手段见 `docs/recon-method.md`（浏览器 fetch/XHR hook，含 body）。

---

## 0. 前提与边界

| 项 | 说明 |
|---|---|
| **授权** | 本项目已获校方允许推进。**使用 `submit` 前请确认你持有校方授权**，否则只读功能可用、写功能不要用 |
| **可撤回性** | ⚠️ **学生侧没有自助撤回接口**。提交后只能请教师「退回修改」（状态回到 `3`）才能重交 |
| **作用范围** | 只能提交**自己的**成果（`studentIds` 填自己的 userId） |
| **测试建议** | 首次使用请让老师建一条测试任务，别拿真实作业试错 |

---

## 1. 三步契约

### 第 1 步 · 上传成果文件

```
POST /api/upload_file/new?fileName=<名>&bucketName=yungu-common&fileSize=<字节数>
                        &fileType=<mime>&fileUrl=taskFile/<毫秒时间戳>_<文件名>
                        &percent=100&uuid=<毫秒时间戳>
Content-Type: multipart/form-data
表单字段名：files
```

| 参数 | 必填 | 说明 |
|---|---|---|
| `fileName` | 是 | 文件名 |
| `bucketName` | 是 | 实测固定 `yungu-common` |
| `fileSize` | 是 | 字节数 |
| `fileType` | 是 | MIME，如 `text/plain`、`application/pdf` |
| `fileUrl` | 是 | **OSS objectKey，由客户端自己算**：`taskFile/<ts>_<fileName>` |
| `percent` | 是 | 实测恒为 `100` |
| `uuid` | 是 | 与 `fileUrl` 里同一个 `<ts>` |

响应（实测）：

```json
{"ifLogin":true,"status":true,"message":"操作成功","code":0,
 "content":{"fileId":11007051,"fileName":"probe-response-check.txt",
            "url":"/api/preview_file?id=11007051",
            "previewImage":"/api/file/preview?previewId=370281",
            "type":"txt",
            "downloadUrl":"https://task.yungu.org/api/new_download_file?id=11007051",
            "sourceFileUrl":"/api/preview_source_file?id=11007051",
            "storeMeta":null,"fileExtends":null,"quizQuestionIds":[],"hasQuiz":false}}
```

→ **只要拿 `content.fileId`**，后面提交用。

> 上传是**服务端代理**（不是前端直传 OSS），所以不需要实现 OSS 签名。
> `/api/sts/token` 虽然存在，但学生提交链路没走它。

### 第 2 步 · 提交

```
POST /api/submitAchievementSendMessage
Content-Type: application/json;charset=UTF-8

{"courseId":18349,
 "fileList":[11006983,11006958],
 "studentIds":[<student-id>],
 "teamList":null,
 "taskPublishId":91958,
 "taskUserRelationId":4458494,
 "textStatus":0}
```

| 字段 | 来源 |
|---|---|
| `courseId` | `getAchievementDetail` 响应的 `courseId` |
| `fileList` | 第 1 步拿到的 `fileId` 数组 |
| `studentIds` | **自己的** userId 数组（`achievementUserResponse.userId`） |
| `teamList` | 实测 `null` |
| `taskPublishId` | 任务发布 ID |
| `taskUserRelationId` | 即 `captureId`，来自 `getAchievementDetail` |
| `textStatus` | 实测有附件提交时为 `0` |

响应：`{"status":true,"code":0,"message":"成功","content":null}`

> ⚠️ **不是 `/api/capture/submitCapture`** —— 那个是**教师端发布任务**用的。
> 光看接口名一定会选错。学生提交走的是 `submitAchievementSendMessage`。

### 第 3 步 · 回读断言（不要只信 HTTP 200）

```
POST /api/student/getAchievementDetail     body: {"taskPublishId":91958}
```

看 `content.achievementStatus`：

| 值 | 含义 | 可否提交 |
|---|---|---|
| `1` | 未交 | ✅ |
| `3` | 待修改（教师退回） | ✅ |
| `4` | 已交 | ❌ |
| `2` | 教师已确认 | ❌ |

提交成功后该值变 `4`，且 `achievementId` 会被分配（实测 `null → 851772`）。

---

## 2. 一个容易踩的行为细节

**应用会把之前上传过、但尚未提交的附件一并带上。** 实测提交时 `fileList` 里有两个 fileId，
其中一个是上一轮"只上传没提交"留下的。所以：

- 你在页面上取消提交后，服务器里已经存了那个文件（只是没绑定到成果）
- 再次提交时它会跟着一起进 `fileList`

脚本默认**复刻应用这个行为**（合并已有 + 新上传）；想只发本次的文件，加 `--only-new`。

---

## 3. 脚本用法

```bash
# ① 先看（默认 dry-run：一个字节都不发）
python3 yungu_tasks.py submit --task 91958 --file ./hw.pdf

# ② 确认无误后真提交（会再要一次交互确认）
python3 yungu_tasks.py submit --task 91958 --file ./hw.pdf --yes

# 只发本次文件，不带上历史附件
python3 yungu_tasks.py submit --task 91958 --file ./hw.pdf --only-new --yes
```

脚本的保护顺序（**每一步都在写之前**）：

1. 读现状 → 状态不在 `{1,3}` 直接拒绝（不会替你绕过教师退回机制）
2. `needEnclosure=true` 但没给 `--file` → 拒绝
3. 身份字段（`courseId`/`taskPublishId`/`taskUserRelationId`/`userId`）缺任何一个 → **在上传之前**拒绝
   （避免在学校存储里留下孤儿文件）
4. 无 `--yes` → 只打印将要发送的 payload
5. 有 `--yes` 但无 `--skip-confirm` → 交互输入 `yes` 二次确认
6. 提交后回读 `achievementStatus` 断言真的变了，才报成功

---

## 4. 未验证的部分（别当已知用）

| 项 | 状态 |
|---|---|
| 纯文字提交（无附件） | **未实测**。`textStatus` 的取值含义没验证，所以脚本的 `--text` 目前**只记录不提交** |
| 图片 / 拍照 / 录音 / 在线文档 / python编程 / scratch编程 这几类成果 | 未实测。UI 上它们是**不同的入口和 input**（图片走 `accept=".gif,.jpeg,…"` 那个 input），payload 可能不同 |
| 多文件提交 | 未单独验证（`fileList` 本身是数组，实测就是两个） |
| 教师端 `submitCapture` / `insertBatchItemResult` | 未测，也不建议碰（那是批改侧） |

---

## 5. 相关文档

| 文件 | 内容 |
|---|---|
| `docs/api-tasks.md` | 任务列表、状态语义、评论接口 |
| `docs/api-schedule.md` | 课表接口 |
| `docs/recon-method.md` | 这套契约是怎么抓出来的 |
| `docs/script.md` | 全部子命令与选项 |
