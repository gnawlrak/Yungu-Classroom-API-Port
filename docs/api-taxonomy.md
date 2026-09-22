# 接口功能分类（task.yungu.org）

> 共 **1335** 条接口，归入 **19** 个功能域；已归类 **1308/1335**。
> **怎么分的**：按路径语义关键词归类，并**先剥掉服务前缀**再判断
> （否则 `/calendar/api/` 下的接口会全被误判成「课表」—— 这是第一版的真实错误）。
> 这是**路径语义分类**，不等于逐个接口都验证过功能。

## ⚠️ 先看这个：目录不等于全集

| 缺口 | 例子 | 后果 |
|---|---|---|
| 动态拼接的路径 | `/api/student/getAchievementDetail`（字面量只有 teacher 版） | 学生端真实接口可能不在清单里 |
| 独立 bundle 的子应用 | 课表 `/calendar/api/personal/schdedule/templateForPc` | 日程子应用的部分接口缺失 |

→ 已知**实测可用但不在清单**的接口有 4 个（下表已标出）。

## 总览

| 功能域 | 接口数 | 只读 | 写操作 | 这一域能干什么 |
|---|---:|---:|---:|---|
| **课程与教学** | 244 | 174 | 70 | 课程、课节(lesson)、单元、章节、知识点、教案、题库试卷、教学资源 |
| **评价与素养成绩** | 226 | 143 | 83 | 素养指标、评价方案与模板、评分、成绩（GPA/学分）、等级制测验 |
| **家校与反馈** | 150 | 119 | 31 | 家校互通、周反馈计划、导师/班级分组、学生日常 |
| **任务与作业** | 140 | 88 | 52 | 作业/任务的发布、列表、提交、批改、草稿箱。学生看到的是「我的任务」 |
| **学生行为与德育** | 135 | 92 | 43 | 行为记录、徽章、奖惩、班级/宿舍行为统计、早预警 |
| **升学与招生** | 98 | 84 | 14 | 升学规划：目标校、申请记录、文书模板、专业方向、访校 |
| **用户与权限** | 67 | 60 | 7 | 当前用户与身份、ACL 权限、角色、组织/学部/年级/师生名单 |
| **统计与看板** | 52 | 42 | 10 | 各类统计报表与看板（出勤/行为/课程/班级/年级/学部） |
| **课表与日程** | 50 | 39 | 11 | 课表(智能课表)、学期/学年、日程、教学计划、时间机器(按日回看) |
| **考勤与请假** | 35 | 25 | 10 | 出勤记录与统计、请假流程与配置、进出校设置 |
| **其他** | 27 | 14 | 13 | 未能按路径语义归类的杂项 |
| **成长目标与档案** | 27 | 16 | 11 | 成长目标与总结、成长档案、成果墙、高光时刻、活动记录 |
| **文件与媒体** | 21 | 13 | 8 | 文件上传下载、预览、导出、OSS 直传凭证、照片 |
| **阅读** | 20 | 16 | 4 | 阅读记录、阅读统计、书目 |
| **AI 功能** | 12 | 8 | 4 | AI 应用/Agent、AI 备课、AI 批改、AI 话题 |
| **配置与字典** | 12 | 11 | 1 | 全局配置、数据字典、规则、表单、标签 |
| **消息与通知** | 11 | 9 | 2 | 站内消息、通知、告警、催办 |
| **互动与点赞** | 6 | 1 | 5 | 点赞、评论、印象互动 |
| **健康与体育** | 2 | 1 | 1 | 体测数据、健康问卷、周期体检与 AI 建议 |

> 「写操作」按路径动词（add/update/delete/submit/import/send…）识别，**不要随意调用**。

---

## 学生视角：实测可用的接口 ★

用**你自己的学生账号**真实调通并核对过返回的（不是推断）：

| 接口 | 用途 | 功能域 |
|---|---|---|
| `/api/getAllTasks` | 任务列表 ★ | 任务与作业 |
| `/api/taskPublish/getTaskCountForStudent` | 任务计数 ★ | 任务与作业 |
| `/api/student/getAchievementDetail` | 任务详情 + **教师评论** ★（**不在目录：动态拼接**） | —（不在目录） |
| `/api/getMixedPublishDetail` | 任务元信息 ★ | 任务与作业 |
| `/calendar/api/personal/schdedule/templateForPc` | 课表 ★（**不在目录：独立 bundle**） | —（不在目录） |
| `/calendar/api/current/user` | 日程子应用身份 ★（**不在目录**） | —（不在目录） |
| `/calendar/api/teaching/allStageGrade` | 学部年级表 ★（**不在目录**） | —（不在目录） |
| `/api/currentUser` | 当前用户 ★ | 用户与权限 |
| `/api/my/currentCourses` | 我的课程 ★ | 课程与教学 |
| `/api/course/listCoursesBySemId` | 学期课程 ★ | 课程与教学 |
| `/api/listYearAndSemester` | 学年学期 ★ | 课表与日程 |
| `/api/schoolYear` | 学年 ★ | 课表与日程 |
| `/api/capture/getTypeWork` | 成果类型字典 ★ | 任务与作业 |

集中在「任务与作业」「课表与日程」「用户与权限」三域 —— 即「我的任务」和「我的日程」两个页面。

---

## 课程与教学（244 条：只读 174 / 写 70）

课程、课节(lesson)、单元、章节、知识点、教案、题库试卷、教学资源

**主要子模块**：`user`(26)　`statistics`(16)　`lesson`(14)　`chapter`(9)　`course`(9)　`get`(7)　`plan`(7)　`bind`(6)

**代表性只读接口**：

- `GET /api/acl/courseList`
- `GET /api/all/course`
- `GET /api/all/course/grades`
- `GET /api/all/teacher`
- `GET /api/board/courseKanBan`
- `GET /api/board/courseKanBanBySubject`
- `GET /api/board/courseKanBanByTree`
- `GET /api/board/getTeacherUserByName`
- `GET /api/chapter/getClassify`
- `GET /api/chapter/getFileListByChapterId`
- `GET /api/chapter/getFilePageByChapterId`
- `GET /api/chapter/getMyFilePageByChapterId`
- … 另有 162 个只读接口，见 `yungu_api_catalog.md`

⚠️ 写操作 70 个（如 `openLesson`、`addCourseResources`、`addQualityLesson`、`addResourcesFile`、`chapter`、`group`）—— 本文档与脚本都不会调用它们。

---

## 评价与素养成绩（226 条：只读 143 / 写 83）

素养指标、评价方案与模板、评分、成绩（GPA/学分）、等级制测验

**主要子模块**：`power`(37)　`evaluation`(26)　`template`(23)　`indicator`(22)　`user`(18)　`standardizedTest`(11)　`achievement`(5)　`gradeManagement`(5)

**代表性只读接口**：

- `GET /api/achievement/result/growthRecord/count`
- `POST /api/achievement/resultWallFlow`
- `POST /api/achievement/result_wall`
- `GET /api/achievementOperation`
- `GET /api/board/evaluationPlanDataBoard`
- `GET /api/board/evaluationPlanList`
- `GET /api/board/habitEvaluationPlanList`
- `GET /api/comprehensivePerformance`
- `GET /api/determineReview/myUploadData`
- `GET /api/determineReview/studentAssessmentData`
- `POST /api/elementResult/forcedLock`
- `POST /api/elementResult/getLock`
- … 另有 131 个只读接口，见 `yungu_api_catalog.md`

⚠️ 写操作 83 个（如 `auditStatistics`、`audit_list`、`addGraduationCriteria`、`evaluationPlanDataBoard`、`copyGraduationCriteria`、`deleteGraduationCriteria`）—— 本文档与脚本都不会调用它们。

---

## 家校与反馈（150 条：只读 119 / 写 31）

家校互通、周反馈计划、导师/班级分组、学生日常

**主要子模块**：`homeSchool`(33)　`feedback`(26)　`recipe`(20)　`statistics`(13)　`student`(12)　`team`(11)　`home-school`(3)　`new`(3)

**代表性只读接口**：

- `GET /api//selectAllTutor`
- `GET /api/board/groupList`
- `未知 /api/board/groupListReport`
- `GET /api/feedback/checkCreatePlanAuthority`
- `未知 /api/feedback/download/template`
- `GET /api/feedback/getNotificationReceiver`
- `GET /api/feedback/gradeByStage`
- `GET /api/feedback/gradeList`
- `GET /api/feedback/groupByGrade`
- `GET /api/feedback/groupList`
- `GET /api/feedback/listDownloadWeekFeedbackPdfJob`
- `GET /api/feedback/moduleList`
- … 另有 107 个只读接口，见 `yungu_api_catalog.md`

⚠️ 写操作 31 个（如 `feedbackList`、`auditFeedbackDetail`、`deleteById`、`importData`、`importNum`、`insertDownloadWeekFeedbackPdfJob`）—— 本文档与脚本都不会调用它们。

---

## 任务与作业（140 条：只读 88 / 写 52）

作业/任务的发布、列表、提交、批改、草稿箱。学生看到的是「我的任务」

**主要子模块**：`capture`(31)　`learn`(26)　`homeworkManagement`(17)　`draft`(6)　`taskPublish`(5)　`task`(4)　`user`(4)　`file-services`(3)

**代表性只读接口**：

- `GET /api/capture`
- `GET /api/capture/findResultWallByCaptureId`
- `GET /api/capture/findTreeView`
- `POST /api/capture/findUserCaptureCount`
- `POST /api/capture/findUserCaptureCountConfig`
- `GET /api/capture/getCaptureByCaptureId`
- `GET /api/capture/getCaptureByCaptureId/report/data`
- `GET /api/capture/getCapturerStudens`
- `GET /api/capture/getRegularLabel`
- `GET /api/capture/getTutorStudentList`
- `GET /api/capture/getTypeWork` ★
- `GET /api/capture/getUploadPhotoPermission`
- … 另有 76 个只读接口，见 `yungu_api_catalog.md`

⚠️ 写操作 52 个（如 `addCaptureLabelRelation`、`addRegularLabel`、`addTypeWorkCaptureRelation`、`auditCapture`、`deleteCaptureById`、`insertBatchItemResult`）—— 本文档与脚本都不会调用它们。

---

## 学生行为与德育（135 条：只读 92 / 写 43）

行为记录、徽章、奖惩、班级/宿舍行为统计、早预警

**主要子模块**：`newBehaviorRecord`(56)　`behaviorRecord`(27)　`statistics`(16)　`dormitoryBehavior`(8)　`classBehaviorRecord`(7)　`behaviorSku`(6)　`rank`(5)　`classBehavior`(3)

**代表性只读接口**：

- `GET /api/moralEduStatistics/CIOMetric`
- `未知 /calendar/api/behaviorRecord/aiAssistant`
- `未知 /calendar/api/behaviorRecord/allStu/behavior/download/template`
- `未知 /calendar/api/behaviorRecord/allStu/behavior/downloadFailData`
- `POST /calendar/api/behaviorRecord/approval`
- `GET /calendar/api/behaviorRecord/approval/detail`
- `GET /calendar/api/behaviorRecord/getOwnChildrenInfo`
- `GET /calendar/api/behaviorRecord/getUserSubject`
- `GET /calendar/api/behaviorRecord/groupAnalyze`
- `POST /calendar/api/behaviorRecord/groupStatistics`
- `GET /calendar/api/behaviorRecord/listBehaviorType`
- `GET /calendar/api/behaviorRecord/listDorms`
- … 另有 80 个只读接口，见 `yungu_api_catalog.md`

⚠️ 写操作 43 个（如 `import`、`importCount`、`create`、`editRecord`、`export`、`saveOrUpdatePunishment`）—— 本文档与脚本都不会调用它们。

---

## 升学与招生（98 条：只读 84 / 写 14）

升学规划：目标校、申请记录、文书模板、专业方向、访校

**主要子模块**：`enrolmentPlan`(98)

**代表性只读接口**：

- `GET /api/enrolmentPlan/acl`
- `GET /api/enrolmentPlan/alreadyStages`
- `POST /api/enrolmentPlan/alumnusList`
- `POST /api/enrolmentPlan/applyRecordAddOrUpdate`
- `GET /api/enrolmentPlan/applyRecordApplyTimeType`
- `GET /api/enrolmentPlan/applyRecordById`
- `POST /api/enrolmentPlan/applyRecordDelete`
- `未知 /api/enrolmentPlan/applyRecordDownload`
- `GET /api/enrolmentPlan/applyRecordDownloadErrorInfo`
- `GET /api/enrolmentPlan/applyRecordDownloadErrorInfoUpdate`
- `GET /api/enrolmentPlan/applyRecordDownloadStudent`
- `GET /api/enrolmentPlan/applyRecordEnrollResultType`
- … 另有 72 个只读接口，见 `yungu_api_catalog.md`

⚠️ 写操作 14 个（如 `batchDeleteTargetSchool`、`deleteSpecialtyById`、`deleteTargetSchool`、`exportTargetSchoolByTeacher`、`addOrUpdate`、`batchUpload`）—— 本文档与脚本都不会调用它们。

---

## 用户与权限（67 条：只读 60 / 写 7）

当前用户与身份、ACL 权限、角色、组织/学部/年级/师生名单

**主要子模块**：`user`(11)　`studentManagement`(5)　`acl`(4)　`student`(4)　`school`(3)　`public`(2)　`all`(2)　`current`(2)

**代表性只读接口**：

- `未知 /agent-max/api/public/assistants/by-school/`
- `GET /api/acl/adminClassList`
- `GET /api/acl/gradeList`
- `GET /api/acl/stageList`
- `GET /api/acl/subjectList`
- `GET /api/all/grade`
- `GET /api/check/permission`
- `GET /api/checkPermission`
- `GET /api/checkPermissions`
- `GET /api/current/user/identity`
- `GET /api/currentIdentity`
- `GET /api/currentUser` ★
- … 另有 48 个只读接口，见 `yungu_api_catalog.md`

⚠️ 写操作 7 个（如 `export_student`、`saveSchoolConfig`、`save`、`updateUserHobby`、`updateIsPublic`、`list`）—— 本文档与脚本都不会调用它们。

---

## 统计与看板（52 条：只读 42 / 写 10）

各类统计报表与看板（出勤/行为/课程/班级/年级/学部）

**主要子模块**：`statistics`(30)　`analytics`(6)　`board`(4)　`getLearningOverviewConfig`(2)　`user`(2)　`fake_chart_data`(1)　`ifEditStuBoardPermission`(1)　`listLearningOverview`(1)

**代表性只读接口**：

- `未知 /api/analytics`
- `GET /api/analytics/report`
- `GET /api/analytics/report/cioAuthority`
- `GET /api/analytics/reportByClientType`
- `GET /api/analytics/reportByClientTypeWithUserDetail`
- `GET /api/analytics/reportBySchool`
- `GET /api/board`
- `GET /api/board/getTobeDoneUserInfo`
- `GET /api/board/gradeList`
- `GET /api/board/gradeListByTree`
- `GET /api/fake_chart_data`
- `GET /api/getLearningOverviewConfig`
- … 另有 30 个只读接口，见 `yungu_api_catalog.md`

⚠️ 写操作 10 个（如 `saveModuleContentOfStuBoard`、`export`、`export`、`export`、`export`、`export`）—— 本文档与脚本都不会调用它们。

---

## 课表与日程（50 条：只读 39 / 写 11）

课表(智能课表)、学期/学年、日程、教学计划、时间机器(按日回看)

**主要子模块**：`plan`(20)　`homeSchool`(5)　`all`(3)　`board`(2)　`growthRecord`(2)　`schoolYear`(2)　`timeMachine`(2)　`statistics`(2)

**代表性只读接口**：

- `GET /api/all/semester`
- `GET /api/board/getMonthBySemester`
- `GET /api/board/getYearAndSemesterList`
- `GET /api/currentSemester/rangeTime`
- `GET /api/currentStageList`
- `GET /api/currentTimeToSemester`
- `GET /api/get/semester`
- `GET /api/getSemesterByYearId`
- `GET /api/growthRecord/bySemester`
- `GET /api/growthRecord/semesterList`
- `GET /api/homeSchool/chiefTutorInfoByStudentAndSemester`
- `GET /api/homeSchool/currentSemesterId`
- … 另有 27 个只读接口，见 `yungu_api_catalog.md`

⚠️ 写操作 11 个（如 `addOrUpdate`、`addOrUpdateWeek`、`delete`、`deleteDay`、`deleteWeek`、`sendDayPlanMessage`）—— 本文档与脚本都不会调用它们。

---

## 考勤与请假（35 条：只读 25 / 写 10）

出勤记录与统计、请假流程与配置、进出校设置

**主要子模块**：`school`(9)　`leaveConfig`(7)　`statistics`(5)　`leaveFlow`(3)　`leave`(2)　`batchUpdateStudentAttendanceDetail`(1)　`checkAttendanceSetting`(1)　`listAttendanceStatus`(1)

**代表性只读接口**：

- `POST /api/leave/reasonReviewApprove`
- `GET /api/leaveConfig/list`
- `GET /calendar/api/checkAttendanceSetting`
- `GET /calendar/api/listAttendanceStatus`
- `POST /calendar/api/listDormAttendance`
- `POST /calendar/api/listStudentAttendanceDetail`
- `POST /calendar/api/listStudentsAttendance`
- `POST /calendar/api/query/listAttendanceStudent`
- `GET /calendar/api/showAttendanceSetting`
- `POST /calendar/api/statistics/leaveStatistics`
- `GET /calendar/api/statistics/leaveStatisticsSwitch`
- `POST /calendar/api/statistics/listAttendanceStatistics`
- … 另有 13 个只读接口，见 `yungu_api_catalog.md`

⚠️ 写操作 10 个（如 `update`、`batchUpdateStudentAttendanceDetail`、`exportStudentClassAttendanceStatistics`、`updateStudentAttendanceDetail`、`setEnteringLeavingSetting`、`updateAttendance`）—— 本文档与脚本都不会调用它们。

---

## 其他（27 条：只读 14 / 写 13）

未能按路径语义归类的杂项

**主要子模块**：`habit`(4)　`public`(1)　`activities`(1)　`transcloudIntegralList`(1)　`updateDescription`(1)　`updatePersonDefault`(1)　`checkCCA`(1)　`deleteCommonPhrasesById`(1)

**代表性只读接口**：

- `未知 /agent-max/api/public/pagelab/tools`
- `GET /api/activities`
- `GET /api/transcloudIntegralList`
- `GET /calendar/api/checkCCA`
- `GET /calendar/api/getCommonPhrases`
- `GET /calendar/api/getCommonPhrasesClassification`
- `GET /calendar/api/query/statusStatistic`
- `GET /calendar/api/search/grades`
- `POST /calendar/api/stuDayAnalyze`
- `未知 /center/api/general/translate`
- `POST /course/api/chooseBySubject`
- `GET /evaluation/api/habit/listHabitTree`
- … 另有 2 个只读接口，见 `yungu_api_catalog.md`

⚠️ 写操作 13 个（如 `updateDescription`、`updatePersonDefault`、`deleteCommonPhrasesById`、`deleteCommonPhrasesClassificationById`、`count`、`saveCommonPhrases`）—— 本文档与脚本都不会调用它们。

---

## 成长目标与档案（27 条：只读 16 / 写 11）

成长目标与总结、成长档案、成果墙、高光时刻、活动记录

**主要子模块**：`growthRecord`(5)　`target`(5)　`board`(2)　`user`(2)　`addImpression`(1)　`agreedImpression`(1)　`deleteImpression`(1)　`deletedActivity`(1)

**代表性只读接口**：

- `POST /api/agreedImpression`
- `GET /api/board/recordInfoList`
- `未知 /api/board/recordInfoListReport`
- `GET /api/getActivity`
- `GET /api/growthRecord`
- `未知 /api/growthRecord/board/gradeList`
- `未知 /api/growthRecord/board/groupList`
- `GET /api/growthRecord/honorTypeList`
- `GET /api/growthRecord/kindergartenTemplate`
- `GET /api/homeSchool/studentGrowthAim`
- `GET /api/isDeletedActivity`
- `GET /api/poster/info`
- … 另有 4 个只读接口，见 `yungu_api_catalog.md`

⚠️ 写操作 11 个（如 `addImpression`、`deleteImpression`、`deletedActivity`、`insertActivity`、`delete`、`create`）—— 本文档与脚本都不会调用它们。

---

## 文件与媒体（21 条：只读 13 / 写 8）

文件上传下载、预览、导出、OSS 直传凭证、照片

**主要子模块**：`photo`(3)　`fileContent`(2)　`upload_file`(2)　`batch`(1)　`demoExport`(1)　`file`(1)　`getFileBatch`(1)　`imageRotate`(1)

**代表性只读接口**：

- `GET /api/demoExport`
- `未知 /api/file/preview`
- `GET /api/fileContent/list`
- `GET /api/fileContent/selectByFileId`
- `未知 /api/getFileBatch`
- `未知 /api/new_download_file`
- `GET /api/photo/downloadFile`
- `未知 /api/photo/preview_file`
- `未知 /api/preview_file`
- `GET /api/record/screen/file/list`
- `GET /api/sts/token`
- `GET /calendar/api/stuDayExportCode`
- … 另有 1 个只读接口，见 `yungu_api_catalog.md`

⚠️ 写操作 8 个（如 `new`、`updateImageRotate`、`batchUploadTemplate`、`update_fileName`、`shareFile`、`upload_file`）—— 本文档与脚本都不会调用它们。

---

## 阅读（20 条：只读 16 / 写 4）

阅读记录、阅读统计、书目

**主要子模块**：`read`(5)　`export`(2)　`messageCenter`(2)　`readRecord`(2)　`addReadComment`(1)　`deletedReadComment`(1)　`getMyReadBooks`(1)　`getMyReadInfo`(1)

**代表性只读接口**：

- `GET /api/getMyReadBooks/byMonth`
- `GET /api/getMyReadInfo/byRange`
- `GET /api/getMyReadStatistics`
- `POST /api/messageCenter/read`
- `GET /api/messageCenter/readAll`
- `GET /api/read/detailById`
- `GET /api/read/dynamicList`
- `GET /api/read/listStatistics`
- `GET /api/read/statistics`
- `GET /api/read/yesterdayStatistics`
- `GET /api/readBooks/byRange`
- `GET /api/readData/statistics`
- … 另有 4 个只读接口，见 `yungu_api_catalog.md`

⚠️ 写操作 4 个（如 `addReadComment`、`deletedReadComment`、`statistics`、`readRecord`）—— 本文档与脚本都不会调用它们。

---

## AI 功能（12 条：只读 8 / 写 4）

AI 应用/Agent、AI 备课、AI 批改、AI 话题

**主要子模块**：`prefixPrompt`(2)　`ai`(1)　`createOrEditAITopic`(1)　`getAIApps`(1)　`getAIConversionForTopic`(1)　`getAITopicsList`(1)　`getDetail`(1)　`getPrefixPromptPersonFlag`(1)

**代表性只读接口**：

- `GET /api/ai/grade/list`
- `未知 /api/getAIApps`
- `GET /api/getAIConversionForTopic`
- `GET /api/getAITopicsList`
- `GET /api/getDetail`
- `GET /api/getPrefixPromptPersonFlag`
- `GET /api/prefixPrompt/list`
- `POST /calendar/api/stu/detail/analyzeJSONExplain`

⚠️ 写操作 4 个（如 `createOrEditAITopic`、`update`、`saveAIConversionForTopic`、`batchCreateAIResultByPlanId`）—— 本文档与脚本都不会调用它们。

---

## 配置与字典（12 条：只读 11 / 写 1）

全局配置、数据字典、规则、表单、标签

**主要子模块**：`1`(1)　`appValueConfig`(1)　`config`(1)　`dict`(1)　`fake_list`(1)　`forms`(1)　`mock`(1)　`model`(1)

**代表性只读接口**：

- `GET /api/1/item/`
- `GET /api/appValueConfig`
- `GET /api/config/get`
- `GET /api/dict/hobby`
- `GET /api/fake_list`
- `POST /api/forms`
- `GET /api/mock/changeAccount`
- `GET /api/model/list`
- `GET /api/queryEdit`
- `GET /api/rule`
- `GET /api/tags`

⚠️ 写操作 1 个（如 `set_language`）—— 本文档与脚本都不会调用它们。

---

## 消息与通知（11 条：只读 9 / 写 2）

站内消息、通知、告警、催办

**主要子模块**：`messageCenter`(4)　`alarm`(1)　`conversation`(1)　`hurry`(1)　`listChatGPTUsageAmountBySchoolId`(1)　`notices`(1)　`project`(1)　`school`(1)

**代表性只读接口**：

- `POST /api/conversation`
- `GET /api/listChatGPTUsageAmountBySchoolId`
- `GET /api/messageCenter/count`
- `GET /api/messageCenter/page`
- `未知 /api/messageCenter/pageAll`
- `GET /api/notices`
- `GET /api/project/notice`
- `GET /course/api/school/getMessageRemainingCount`
- `GET /message/api/messageCenter/v2/page`

⚠️ 写操作 2 个（如 `alarm`、`hurry`）—— 本文档与脚本都不会调用它们。

---

## 互动与点赞（6 条：只读 1 / 写 5）

点赞、评论、印象互动

**主要子模块**：`addLike`(1)　`cancelZan`(1)　`deletedCommentary`(1)　`deletedLike`(1)　`saveCommentary`(1)　`saveZan`(1)

**代表性只读接口**：

- `POST /api/cancelZan`

⚠️ 写操作 5 个（如 `addLike`、`deletedCommentary`、`deletedLike`、`saveCommentary`、`saveZan`）—— 本文档与脚本都不会调用它们。

---

## 健康与体育（2 条：只读 1 / 写 1）

体测数据、健康问卷、周期体检与 AI 建议

**主要子模块**：`health`(2)

**代表性只读接口**：

- `GET /health/api/health/periodic-review/aiDetail`

⚠️ 写操作 1 个（如 `updateHealthAIAdvice`）—— 本文档与脚本都不会调用它们。

---

## 局限

1. **路径语义分类**，不代表接口真实行为。
2. **参数与响应未逐个验证** —— 只有 `docs/api-tasks.md` / `docs/api-schedule.md` 里的接口是逐字段核对过的。
3. **权限未逐个测**。只有上表 ★ 的 13 个确认学生账号可调；其余多为教师端/管理端。
4. **写操作一律未调用**（安全红线）。
