# Yungu Classroom API Port

对 **云谷课堂（task.yungu.org）** 学生端接口的逆向整理与客户端。

包含一份 **1345 条接口**的功能目录（构建号 `20260922090917`）、四份逐字段核对过的接口契约文档，以及一套可复用的接口侦察方法。

> 本项目是**接口性质的逆向整理**，与学校官方无关，非官方文档。
> **本项目在学校的知情与允许下推进。**

---

## ⚠️ 免责声明（请先读）

1. **仅供学习与研究。** 记录的是「前端产物里能看到的接口形状」，用于理解一个真实 SPA 的前后端契约。
2. **默认只读。** 除 `submit` 外，仓库内所有代码只发查询请求（GET / 空 body 的查询类 POST），不含任何修改、删除操作。
   `submit` 是唯一的写操作入口：它**默认 dry-run，一个字节都不发**，必须显式 `--yes` 并交互确认后才提交；
   它只调用**一个已实测**的写端点 `/api/submitAchievementSendMessage`，且**只作用于自己的任务**。
3. **不绕过鉴权。** 全部操作使用**使用者自己的账号会话**。项目里没有口令爆破、越权访问或漏洞利用。
4. **不要用它访问他人的数据。** 用别人的账号、或读取他人信息，可能违法，也与本项目无关。
5. **接口目录是"发现结果"，不是官方文档。** 站点会不定期重新部署，接口数与字段会变 —— 本仓库对应构建号
   `20260922090917`，重新抓一次即可（`python3 yungu_tasks.py recon`）。
6. **请遵守学校的服务条款。** 代码内置限流：`--sleep`（默认 0.3s）与 `--max-requests`（默认 300），请勿调到给系统造成压力的程度。
7. **数据属于学校。** 学生成绩、教师评语等均为他人/机构的财产，请勿二次传播。
8. **重交没有平台限制，但撤回做不到。** 实测：对本人任务重交**随时可以**，服务器不看任务状态、
   也不需要教师退回；每次重交会**新建一个成果版本**（`achievementId` 变化），教师看到的是最新版。
   但**没有接口能把自己改回「未交」**，旧版本也不能自助删除 —— 所以脚本默认只对「未交/待修改」放行，
   要重交已交成果需显式 `--resubmit`。这是客户端的保守选择，不是平台约束。
   本项目的提交契约是在教师**专门创建的测试任务**上验证的 —— 请同样不要拿真实作业试错。
9. 作者不对任何误用后果负责。**若校方要求，会立即删除本仓库。**

---

## 能力一览

| 能力 | 类型 | 说明 |
|---|---|---|
| 剩余任务 | 读 | 清单、状态（未交/待修改/已交/已确认）、截止、是否逾期 |
| 教师评论 | 读 | 评论正文、作者、时间、回复关系 —— **并标明属于哪个任务** |
| 课表 | 读 | 周视图：时间、课程、教室、教师、学科、颜色 |
| **提交成果** | **写** | 上传文件并提交任务。**默认 dry-run**，需 `--yes` + 交互确认 + 校方授权 |
| 接口目录 | 静态 | 1345 条，19 个功能域，标注 HTTP 方法与「疑似写操作」 |
| 侦察方法 | 文档 | 静态提取 + 浏览器 hook 的完整可跑配方 |

## 这不是什么

- ❌ 不是官方 API 文档（学校没有公开 API）
- ❌ 不是通用写操作客户端：**只实现了 1 个写端点**，其余 381 个写接口一律不调用
- ❌ 拿不到加密字段（例如学情总览里的 `totalScore` 是前端解密的密文）
- ❌ 没有批量代交、没有绕过权限的路径

---

## 快速开始

只需要 **Python 3 标准库**，无需 `pip install`。

```bash
git clone https://github.com/gnawlrak/Yungu-Classroom-API-Port.git
cd Yungu-Classroom-API-Port

# 1) 从你自己的浏览器取会话 Cookie
#    登录 task.yungu.org → F12 → Network → 任一 /api/ 请求
#    → Headers → Request Headers → 复制 Cookie 整行
echo '把复制的 Cookie 粘到这里' > cookie.txt
chmod 600 cookie.txt

# 2) 只读功能
python3 yungu_tasks.py tasks        # 剩余任务
python3 yungu_tasks.py comments     # 教师评论（标明归属任务）
python3 yungu_tasks.py timetable    # 本周课表
```

`cookie.txt` 与脚本同级即可被自动找到。**该文件已在 `.gitignore` 中，切勿提交。**

### 提交成果（写操作，需授权）

```bash
# 先看 —— 默认 dry-run，不发任何请求，只打印将要发送的 payload
python3 yungu_tasks.py submit --task 91958 --file ./hw.pdf

# 确认无误后真提交（还会要求交互输入 yes）
python3 yungu_tasks.py submit --task 91958 --file ./hw.pdf --yes
```

上传是**三步**（取 OSS 凭证 → 签名 PUT 直传字节 → 注册元数据），并且**强制回读校验** ——
字节读不回来就报失败（只做第三步也能拿到 `fileId`，但文件是空的，这个坑踩过）。

想让新版本**不再包含**某个已交附件：`--drop-file <fileId>` —— 这里的「删除」等于新版本剔除该
`fileId`（旧版本仍在历史里，无法自助删除）。也可用 `--only-new` 只带本次上传的文件。

脚本在**任何写入之前**依次设卡：状态可提交性（`{未交,待修改}`，已交需 `--resubmit`）→ 附件要求 →
身份字段完整性（缺字段会在上传前就拒绝，不会在学校存储里留孤儿文件）→ dry-run → 交互确认 →
提交后**回读状态断言**真的变了才报成功。
契约细节与撤回边界见 [`docs/api-submit.md`](docs/api-submit.md)。

---

## 文档索引

| 文档 | 内容 |
|---|---|
| [`docs/overview.md`](docs/overview.md) | 项目总览：侦察过程、关键发现、注意事项 |
| [`docs/api-tasks.md`](docs/api-tasks.md) | **任务 + 评论**接口契约（49 个字段、状态口径、可跑代码） |
| [`docs/api-schedule.md`](docs/api-schedule.md) | **课表**接口契约（时间窗算法、65 个字段、可跑代码） |
| [`docs/api-submit.md`](docs/api-submit.md) | **提交成果**契约（上传→提交→回读，含撤回边界） |
| [`docs/api-taxonomy.md`](docs/api-taxonomy.md) | 1345 条接口的功能分类（19 个功能域） |
|| [`docs/script.md`](docs/script.md) | 脚本用法：6 个子命令（另有 `task` 别名）、全部选项、退出码、排错 |
| [`docs/recon-method.md`](docs/recon-method.md) | **接口侦察方法**：静态提取 + 浏览器 hook 完整配方 |
| [`yungu_api_catalog.md`](yungu_api_catalog.md) | 1345 条接口目录 |

---

## 仓库结构

```
.
├── yungu_tasks.py                  主脚本（仅标准库）
├── yungu_api_catalog.md            1345 条接口目录（按功能域→模块）
├── yungu_endpoints.json            同上机读版（method/service/module/category/mutating）
├── yungu_endpoints_discovered.json recon 实跑输出
├── docs/
│   ├── overview.md                 项目总览
│   ├── api-tasks.md                任务 + 评论接口契约
│   ├── api-schedule.md             课表接口契约
│   ├── api-submit.md               提交成果契约（唯一的写操作）
│   ├── api-taxonomy.md             功能分类
│   ├── script.md                   脚本文档
│   └── recon-method.md             侦察方法
├── .gitignore                      排除 cookie.txt / 原始响应 / 数据库
└── LICENSE                         GPL-3.0
```

---

## 两个诚实的边界

**① 接口目录是「下界」，不是全集。** 静态提取只能拿到 bundle 里的**字面量路径**，两类抓不到：

| 缺口 | 例子 | 原因 |
|---|---|---|
| 动态拼接的路径 | `/api/student/getAchievementDetail` | bundle 里只有 teacher 版是字面量 |
| 独立 bundle 的子应用 | 课表 `/calendar/api/.../templateForPc` | 日程子应用有自己的产物 |

**② 分类是启发式，不是逐个验证。** 只有 `docs/api-tasks.md`、`docs/api-schedule.md`、
`docs/api-submit.md` 里写的那些接口是逐字段/逐请求核对过的，其余**参数与权限未验证**。

一个具体的教训：**看接口名猜会猜错。** 学生提交成果看着像 `/api/capture/submitCapture`，
实测那个是**教师端发布任务**用的，学生提交实际走 `/api/submitAchievementSendMessage`。

---

## 关于数据

- 本仓库**不包含**任何真实个人数据：文档里的姓名、学号、用户 ID、头像地址均已替换为占位符
- 示例中的接口路径与字段名保留原样（否则文档失去意义），但**不含任何可用于登录的凭据**
- 若你在使用中发现仓库里仍有残留的个人信息，请提 issue，会立刻处理

---

## License

[GPL-3.0](LICENSE)
