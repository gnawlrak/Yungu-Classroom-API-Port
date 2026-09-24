# Yungu Classroom API Port

对 **云谷课堂（task.yungu.org）** 学生端接口的逆向整理与客户端。

包含一份 **1345 条接口**的功能目录（构建号 `20260922090917`）、四份逐字段核对过的接口契约文档，以及一套可复用的接口侦察方法。

---

---

## 能力一览

| 能力 | 类型 | 说明 |
|---|---|---|
| 剩余任务 | 读 | 清单、状态（未交/待修改/已交/已确认）、截止、是否逾期 |
| 教师评论 | 读 | 评论正文、作者、时间、回复关系 —— **并标明属于哪个任务** |
| 课表 | 读 | 周视图：时间、课程、教室、教师、学科、颜色 |
| **提交成果** | **写** | 上传文件并提交任务。**默认 dry-run**，需 `--yes` + 交互确认 |
| 接口目录 | 静态 | 1345 条，19 个功能域，标注 HTTP 方法与「疑似写操作」 |
| 侦察方法 | 文档 | 静态提取 + 浏览器 hook 的完整可跑配方 |

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

### 提交成果（写操作）

```bash
# 先看 —— 默认 dry-run，不发任何请求，只打印将要发送的 payload
python3 yungu_tasks.py submit --task 91958 --file ./hw.pdf

# 确认无误后真提交（还会要求交互输入 yes）
python3 yungu_tasks.py submit --task 91958 --file ./hw.pdf --yes
```

上传是**三步**（取 OSS 凭证 → 签名 PUT 直传字节 → 注册元数据），并且**强制回读校验** ——
字节读不回来就报失败（只做第三步也能拿到 `fileId`，但文件是空的，这个坑踩过）。

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
| [`docs/script.md`](docs/script.md) | 脚本用法：6 个子命令、全部选项、退出码、排错 |
| [`docs/cookie.md`](docs/cookie.md) | **会话 Cookie 是怎么自动拿到的**：CDP 读 HttpOnly 的完整配方 + 安全含义 |
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
│   ├── cookie.md                   会话 Cookie 自动获取配方 + 安全含义
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
