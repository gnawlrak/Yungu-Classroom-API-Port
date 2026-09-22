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
| **可撤回性** | ⚠️ **不能把自己改回「未交」**。但**重交随时可以** —— 实测服务器不看状态、也不需要教师退回，每次重交会**新建一个成果版本**（`achievementId` 变化），教师看到的是最新版 |
| **作用范围** | 只能提交**自己的**成果（`studentIds` 填自己的 userId） |
| **测试建议** | 首次使用请让老师建一条测试任务，别拿真实作业试错 |

---

## 1. 三步契约

### 第 1 步 · 上传成果文件（三步，缺一不可）

> ⚠️ **这一步最初被我实现错了，且错得很隐蔽。** 只做第 3 步也能拿到 `status:true` 和
> `fileId`，但**字节根本没上传**，回读该 fileId 是 `404`。
> 判据只能是「**服务器能否把文件读回来**」，不能是"接口返回成功"。

**① 取 OSS 直传凭证**

```
GET /api/sts/token?type=1
```

响应 `content` 字段（实测）：

| 字段 | 说明 |
|---|---|
| `accessKeyId` / `accessSecret` | STS 临时密钥 |
| `stsToken` | STS 安全令牌（较长） |
| `bucketName` | 实测 `yungu-common` |
| `endpoint` | 形如 `oss-cn-hangzhou.aliyuncs.com` |
| `region` / `ossPath` | 区域；对象前缀（实测 `taskFile/`） |

**② 把字节直传 OSS（这是真正的上传）**

```
PUT https://<bucketName>.<endpoint>/<ossPath><毫秒时间戳>_<文件名>
Date: <RFC1123 GMT>
Content-MD5: <md5 的 base64>
Content-Type: <mime>
x-oss-security-token: <stsToken>
Authorization: OSS <accessKeyId>:<签名>
```

签名是阿里云 OSS **V1** 规范（HMAC-SHA1），纯标准库即可实现：

```python
string_to_sign = "PUT\n" + content_md5 + "\n" + content_type + "\n" + date + "\n" \
                 + "x-oss-security-token:" + sts_token + "\n" \
                 + "/" + bucket + "/" + object_key
signature = base64(hmac_sha1(access_secret, string_to_sign))
```

成功返回 `200` 与 `ETag`。

**③ 注册元数据，拿 `fileId`**

```
GET /api/upload_file/new?fileName=<名>&bucketName=<桶>&fileSize=<字节数>
                        &fileType=<mime>&fileUrl=<objectKey>&percent=100&uuid=<时间戳>
```

> 注意是 **GET**（接口目录里本来就是 GET，我曾按"上传应该用 POST"的直觉改错成 POST）。

响应 `content.fileId` 即后续提交要用的 id。

**④ 必做：回读校验**

```
GET /api/preview_file?id=<fileId>
```

返回 `200` 且字节与本地一致，才算上传成功。返回 `404` 就说明**字节没落上去**。

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

> 另观察到应用在上传后还会调
> `GET /api/student/submitAchievementForDrafts?taskUserRelationId=<id>&fileIds=<fid>`，
> 把附件暂存为草稿。**实测不调它也能提交成功**（直接提交时 fileId 已被绑定），
> 所以本脚本不发这个请求 —— 但它解释了为什么"取消提交"后附件仍会留在下次的 `fileList` 里。

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

## 1.5 实测：重交没有平台限制，客户端闸门是脚本自己的选择

在已交的测试任务上做了两次重交实验：

| 提交前 | 提交 | 服务器响应 | 提交后 |
|---|---|---|---|
| `status=4 ifEditStatus=true` | 新文件 | `status:true` | `status=4`，`achievementId` **851772 → 851804**，新附件已绑定 |
| `status=4 ifEditStatus=false` | 另一文件 | `status:true` | `status=4`，`achievementId` **851804 → 851805** |

结论：

- **服务器不看 `achievementStatus`，也不看 `ifEditStatus`**，对本人任务的重交一律接受
- 每次重交**新建一个成果版本**（`achievementId` 递增），教师看到的是最新版本
- `ifEditStatus` **不是静态权限位**，而是"当前是否处于编辑态"的临时门
  （实测：学生进过编辑界面后为 `true`，重交后变回 `false`）
- 因此脚本默认只对 `{1,3}` 放行、对已交要求 `--resubmit`，是**客户端的保守选择**，
  不是平台约束 —— 文档此前把它写成"需教师退回"，是错的

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

1. 读现状 → 状态不在 `{1,3}` 时默认拒绝，需显式 `--resubmit`（实测服务器并不拦，这是脚本的安全默认）
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
