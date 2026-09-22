# Yungu Classroom API Port

对 **云谷课堂（task.yungu.org）** 学生端接口的逆向整理与**只读**客户端。

包含一份 **1345 条接口**的功能目录（构建号 `20260922090917`）、三份逐字段核对过的接口契约文档，以及一套可复用的接口侦察方法。

> 本项目是**个人学习性质的接口整理**，与学校官方无关，非官方文档。

---

## ⚠️ 免责声明（请先读）

1. **仅供学习与研究。** 本项目记录的是「前端产物里能看到的接口形状」，用于理解一个真实 SPA 的前后端契约。
2. **只读。** 仓库内所有代码只发查询请求（GET / 空 body 的查询类 POST），**不包含任何提交、修改、删除操作**。
3. **不绕过鉴权。** 全部数据来自**使用者自己的账号会话**。项目里没有任何口令爆破、越权访问或漏洞利用。
4. **不要用它访问他人的数据。** 用别人的账号、或读取他人信息，可能违法，也与本项目无关。
5. **接口目录是"发现结果"，不是官方文档。** 站点会不定期重新部署，接口数与字段会变 —— 本仓库对应构建号 `https://cdn-assets.yungu.org/task/20260922090917`，重新抓一次即可（`python3 yungu_tasks.py recon`）。
6. **请遵守学校的服务条款。** 批量请求请加限速——代码里默认有 `sleep` 与请求上限，请勿调高到给系统造成压力的程度。
7. **数据属于学校。** 学生成绩、教师评语等均为他人/机构的财产，请勿二次传播。
8. 作者不对任何误用后果负责。**若校方要求，会立即删除本仓库。**

---

## 这是什么

| 能力 | 说明 |
|---|---|
| **剩余任务** | 任务清单、状态（未交/待修改/已交/已确认）、截止时间、是否逾期 |
| **教师评论** | 每条任务下的评论正文、作者、时间、回复关系 —— **并标明评论属于哪个任务** |
| **课表** | 周视图：时间、课程、教室、教师、学科、颜色 |
| 接口目录 | 1345 条，按 19 个功能域分类，标注 HTTP 方法与「疑似写操作」 |
| 侦察方法 | 静态提取 + 浏览器 hook 的完整可跑配方 |

## 这不是什么

- ❌ 不是官方 API 文档（学校没有公开 API）
- ❌ 不是爬虫框架（没有并发、重试、代理池那些）
- ❌ 不能改数据（写操作接口一个都没实现，也建议你别碰）
- ❌ 拿不到加密字段（例如学情总览里的 `totalScore` 是前端解密的密文，直接调接口只能拿到密文）

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

# 2) 跑
python3 yungu_tasks.py tasks        # 剩余任务
python3 yungu_tasks.py comments     # 教师评论（标明归属任务）
python3 yungu_tasks.py timetable    # 本周课表
```

`cookie.txt` 与脚本同级即可，脚本会自动找到它。**该文件已在 `.gitignore` 中，切勿提交。**

### 其他子命令

```bash
python3 yungu_tasks.py tasks --status 1 --page-size 2000   # 全部历史
python3 yungu_tasks.py tasks --overdue                     # 只看逾期
python3 yungu_tasks.py comments --teacher-only             # 只看老师发的
python3 yungu_tasks.py timetable --week 1                  # 下周
python3 yungu_tasks.py probe                               # 各候选接口返回一览
python3 yungu_tasks.py recon                               # 重新枚举接口
```

---

## 文档索引

| 文档 | 内容 |
|---|---|
| [`docs/overview.md`](docs/overview.md) | 项目总览：侦察过程、关键发现、注意事项 |
| [`docs/api-tasks.md`](docs/api-tasks.md) | **任务 + 评论**接口契约（49 个字段、状态口径、可跑代码） |
| [`docs/api-schedule.md`](docs/api-schedule.md) | **课表**接口契约（时间窗算法、65 个字段、可跑代码） |
| [`docs/api-taxonomy.md`](docs/api-taxonomy.md) | 1345 条接口的功能分类（19 个功能域） |
| [`docs/script.md`](docs/script.md) | 脚本用法：子命令、选项、退出码、排错 |
| [`docs/recon-method.md`](docs/recon-method.md) | **接口侦察方法**：静态提取 + 浏览器 hook 完整配方 |
| [`yungu_api_catalog.md`](yungu_api_catalog.md) | 全量接口目录 |

---

## 仓库结构

```
.
├── yungu_tasks.py                  主脚本（仅标准库，~750 行）
├── yungu_api_catalog.md            1345 条接口目录（按功能域→模块）
├── yungu_endpoints.json            同上机读版（method/service/module/category/mutating）
├── yungu_endpoints_discovered.json recon 实跑输出
├── docs/
│   ├── overview.md                 项目总览
│   ├── api-tasks.md                任务 + 评论接口契约
│   ├── api-schedule.md             课表接口契约
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

**② 方法是启发式，不是逐个验证。** 分类按路径语义关键词得出；只有 `docs/api-tasks.md` / `docs/api-schedule.md` 里的十几个接口是逐字段核对过的，其余**参数与响应未验证、权限未测**。

---

## 关于数据

- 本仓库**不包含**任何真实个人数据：文档里的姓名、学号、用户 ID、头像地址均已替换为占位符
- 示例中的接口路径与字段名保留原样（否则文档失去意义），但**不含任何可用于登录的凭据**
- 若你在使用中发现仓库里仍有残留的个人信息，请提 issue，会立刻处理

---

## License

[GPL-3.0](LICENSE)
