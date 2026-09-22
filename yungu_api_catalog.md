# task.yungu.org 对外开放接口目录

- 来源：`https://cdn-assets.yungu.org/task/20260922090917/`（主包 + 615 个 chunk，含 webpack 声明清单里的全部 id）
- 抓取时间对应的构建号：**https://cdn-assets.yungu.org/task/20260922090917**（站点重新部署时会变，接口数会小幅波动）
- 鉴权：CAS SSO；未登录时 `/api/*` 统一返回 `code:1000 / message:"请刷新！"`
- **鉴权过滤器前置于路由**：不存在的接口与真实接口返回同一信封，未登录无法靠探测枚举

## ⚠️ 本目录的两个固有缺口（重要）

1. **只收录 bundle 里的字面量路径**。动态拼接的抓不到 —— 例如学生端的
   `/api/student/getAchievementDetail` 在 bundle 里**没有字面量**（只有 `/api/teacher/getAchievementDetail`），
   它是运行时按身份拼出来的。**该接口实测可用，但不在下面的清单里。**
2. **独立 bundle 的子应用不在内**。日程子应用 `newSchoolCalendar` 有自己的产物，
   所以 `/calendar/api/personal/schdedule/templateForPc`（课表）**也不在目录里**。

> 目录是**下界而非全集**。要确认某接口是否真存在，以「页面实测抓包」为准（见 `docs/recon-method.md`）。

## 统计（1345 条）

| HTTP 方法 | 条数 |
|---|---|
| `GET` | 899 |
| `POST` | 368 |
| `未知` | 75 |
| `PUT` | 3 |

| 只读 | 964 |
| 写操作 | 381 |

| 服务前缀 | 条数 |
|---|---|
| `/api` | 930 |
| `/calendar/api` | 251 |
| `/evaluation/api` | 94 |
| `/iot/api` | 26 |
| `/course/api` | 21 |
| `/leave/api` | 11 |
| `/center/api` | 5 |
| `/agent-max/api` | 2 |
| `/health/api` | 2 |
| `/flashNote/api` | 1 |
| `/task/api` | 1 |
| `/work/api` | 1 |

| 功能域 | 条数 |
|---|---|
| 课程与教学 | 244 |
| 评价与素养成绩 | 236 |
| 家校与反馈 | 147 |
| 学生行为与德育 | 140 |
| 任务与作业 | 138 |
| 升学与招生 | 99 |
| 用户与权限 | 67 |
| 统计与看板 | 53 |
| 课表与日程 | 50 |
| 考勤与请假 | 35 |
| 其他 | 28 |
| 成长目标与档案 | 27 |
| 文件与媒体 | 21 |
| 阅读 | 19 |
| AI 功能 | 12 |
| 配置与字典 | 12 |
| 消息与通知 | 9 |
| 互动与点赞 | 6 |
| 健康与体育 | 2 |

## 全量清单（按功能域 → 模块）

### 课程与教学（244）

**`user`**
- `GET` `/api/user/relation/courseApplicability`
- `POST` `/api/user/relation/deleteMyListenedLesson` ⚠️写
- `未知` `/api/user/relation/ifDirectorOfTeachingOrSubjectChief`
- `POST` `/api/user/relation/lessonDetail`
- `POST` `/api/user/relation/lessonDetailMatch`
- `POST` `/api/user/relation/lessonDetailResolve`
- `GET` `/api/user/relation/lessonList`
- `未知` `/api/user/relation/lessonListPdfExport`
- `GET` `/api/user/relation/lessonListStatistics`
- `GET` `/api/user/relation/lessonRecordList`
- `GET` `/api/user/relation/lessonSchoolConfig`
- `GET` `/api/user/relation/myLessonList`
- `GET` `/api/user/relation/myLessonStatistics`
- `GET` `/api/user/relation/openLessonCalendar`
- `GET` `/api/user/relation/openLessonList`
- `GET` `/api/user/relation/teacherAnalysis`
- `POST` `/api/user/relation/teacherAnalysis/detail`
- `未知` `/api/user/relation/teacherAnalysis/export` ⚠️写
- `POST` `/api/user/relation/teacherAnalysis/filterOptions`
- `POST` `/api/user/relation/teacherAnalysis/list`
- `POST` `/api/user/relation/teacherAnalysis/teacherList`
- `GET` `/api/user/relation/teachingResearchGroup/courseDetail`
- `GET` `/api/user/relation/teachingResearchGroup/courseDetailRecordExport`
- `GET` `/api/user/relation/teachingResearchGroup/honorRoll`
- `GET` `/api/user/relation/teachingResearchGroup/overview`
- `GET` `/api/user/relation/teachingResearchGroup/statistics`
- `GET` `/api/user/relation/teachingResearchGroup/subjectList`
- `GET` `/course/api/user/searchTeacher`

**`statistics`**
- `GET` `/calendar/api/statistics/courseAggregateStatisticsSwitch`
- `POST` `/calendar/api/statistics/courseAttendanceDetail`
- `GET` `/calendar/api/statistics/exportCourseAttendanceDetail` ⚠️写
- `GET` `/calendar/api/statistics/exportCourseAttendanceStatistics` ⚠️写
- `GET` `/calendar/api/statistics/exportTeacherAttendanceStatistics` ⚠️写
- `GET` `/calendar/api/statistics/isShowCourseStatistics`
- `POST` `/calendar/api/statistics/listAttendanceCoursesStatistics`
- `POST` `/calendar/api/statistics/listCourseAttendanceStatistics`
- `POST` `/calendar/api/statistics/listTeacherAttendanceEvents`
- `POST` `/calendar/api/statistics/listTeacherAttendanceStatistics`
- `POST` `/calendar/api/statistics/previewTeacherAttendanceReminder`
- `POST` `/calendar/api/statistics/sendTeacherAttendanceReminder` ⚠️写
- `POST` `/calendar/api/statistics/studentCourseAttendanceRecords`
- `GET` `/calendar/api/statistics/subject/course`
- `GET` `/calendar/api/statistics/teacher/listRevokeTier`
- `GET` `/calendar/api/statistics/userCoursesStatisticsPermission`

**`lesson`**
- `POST` `/api/lesson/addReflectionOrRecord` ⚠️写
- `POST` `/api/lesson/classMode/behaviorCreate`
- `POST` `/api/lesson/classMode/behaviorDetailList`
- `POST` `/api/lesson/classMode/behaviorSummary`
- `GET` `/api/lesson/deleteReflectionOrRecord` ⚠️写
- `GET` `/api/lesson/getGroupListByCourse`
- `GET` `/api/lesson/getReflectionOrRecordByLessonId`
- `GET` `/api/lesson/getTeachingReflectionOrRecord`
- `GET` `/api/lesson/learningSteps/detail`
- `GET` `/api/lesson/lectureRecordAndTeachingReflection`
- `GET` `/api/lesson/listCourseLesson`
- `GET` `/api/lesson/teachingReflectionList`
- `GET` `/api/lesson/updateLessonResourceClassify` ⚠️写
- `POST` `/api/lesson/updateReflectionOrRecord` ⚠️写

**`chapter`**
- `POST` `/api/chapter/addChapter` ⚠️写
- `GET` `/api/chapter/deleteChapterNoChildern` ⚠️写
- `GET` `/api/chapter/getClassify`
- `GET` `/api/chapter/getFileListByChapterId`
- `GET` `/api/chapter/getFilePageByChapterId`
- `GET` `/api/chapter/getMyFilePageByChapterId`
- `GET` `/api/chapter/showAllChapter`
- `POST` `/api/chapter/updateChapter` ⚠️写
- `GET` `/api/chapter/updateFileByChapterId` ⚠️写

**`course`**
- `GET` `/api/course`
- `GET` `/api/course/bySubjectId`
- `GET` `/api/course/byTeacherIdList`
- `GET` `/api/course/getAllClassesByCourse`
- `GET` `/api/course/groups`
- `GET` `/api/course/lessonList/byTeacherIdList`
- `GET` `/api/course/listCoursesBySemId`
- `GET` `/api/course/student/all`

**`get`**
- `GET` `/api/get/AI/lesson/listenSummary`
- `GET` `/api/get/AI/lesson/listenSummary/openFlag`
- `POST` `/api/get/AI/makePaperRequest`
- `POST` `/api/get/AI/prepareLesson`
- `GET` `/api/get/openLesson`
- `GET` `/api/get/openLessonList`
- `GET` `/api/get/openLessonMatchCandidates`

**`openLesson`**
- `GET` `/api/openLesson`
- `GET` `/api/openLesson/exportList` ⚠️写
- `GET` `/api/openLesson/getUserByCourseId`
- `GET` `/api/openLesson/listLessonOpenClassification`
- `GET` `/api/openLesson/monthlyStatistics`
- `GET` `/api/openLesson/options`
- `GET` `/api/openLesson/permission`

**`plan`**
- `POST` `/api/plan/addOrUpdateCourse` ⚠️写
- `GET` `/api/plan/checkUserIsDirectorOfTeaching`
- `GET` `/api/plan/deleteCourse` ⚠️写
- `GET` `/api/plan/getOpenCourseStageList`
- `GET` `/api/plan/listCourse`
- `POST` `/api/plan/queryCourseDefault`
- `POST` `/api/plan/saveCourseDefault` ⚠️写

**`bind`**
- `GET` `/api/bind/lesson/chapter` ⚠️写
- `GET` `/api/bind/lesson/group` ⚠️写
- `GET` `/api/bind/lesson/knowledge` ⚠️写
- `GET` `/api/bind/lesson/teacher` ⚠️写
- `GET` `/api/bind/unit/chapter` ⚠️写
- `GET` `/api/bind/unit/knowledge` ⚠️写

**`knowledge`**
- `POST` `/api/knowledge/addKnowledge` ⚠️写
- `GET` `/api/knowledge/deleteKnowledge` ⚠️写
- `GET` `/api/knowledge/getStageAndSubjectList`
- `GET` `/api/knowledge/getTeachingMaterial`
- `GET` `/api/knowledge/list`
- `POST` `/api/knowledge/updateKnowLedge` ⚠️写

**`exam`**
- `POST` `/api/exam/board/resourceKanban`
- `GET` `/api/exam/board/resourceKanban/export` ⚠️写
- `GET` `/api/exam/delete` ⚠️写
- `GET` `/api/exam/getExamListByPaperId`
- `POST` `/api/exam/save/calPercentOrFraction` ⚠️写

**`paper`**
- `GET` `/api/paper/delete` ⚠️写
- `GET` `/api/paper/detail`
- `GET` `/api/paper/listExamPaper`
- `GET` `/api/paper/status`
- `GET` `/api/paper/type/list`

**`teacher`**
- `GET` `/api/teacher/listUnitUnderPageHome`
- `POST` `/api/teacher/resource/create` ⚠️写
- `GET` `/api/teacher/resource/delete` ⚠️写
- `GET` `/api/teacher/resource/edit` ⚠️写
- `GET` `/api/teacher/resource/type/list`

**`unit`**
- `GET` `/api/unit/group/class/add` ⚠️写
- `GET` `/api/unit/group/class/list`
- `GET` `/api/unit/group/class/remove` ⚠️写
- `GET` `/api/unit/group/student`
- `GET` `/api/unit/listGroup`

**`board`**
- `GET` `/api/board/courseKanBan`
- `GET` `/api/board/courseKanBanBySubject`
- `GET` `/api/board/courseKanBanByTree`
- `GET` `/api/board/getTeacherUserByName`

**`feedback`**
- `GET` `/api/feedback/courseFillInfo`
- `GET` `/api/feedback/courseFillInfoByNum`
- `POST` `/api/feedback/courseFillInfoCreate`
- `POST` `/api/feedback/courseFillInfoUpdate`

**`newBehaviorRecord`**
- `POST` `/calendar/api/newBehaviorRecord/groupStudentByCourse`
- `GET` `/calendar/api/newBehaviorRecord/index/getTeacher`
- `POST` `/calendar/api/newBehaviorRecord/listStudentByCourse`
- `GET` `/calendar/api/newBehaviorRecord/listTeacherInfo`

**`question`**
- `POST` `/api/question/knowledge/importByStageAndSubject` ⚠️写
- `GET` `/api/question/knowledge/list`
- `GET` `/api/question/newGrade/list`
- `GET` `/api/question/subject/list`

**`unbind`**
- `GET` `/api/unbind/lesson/chapter` ⚠️写
- `GET` `/api/unbind/lesson/knowledge` ⚠️写
- `GET` `/api/unbind/unit/chapter` ⚠️写
- `GET` `/api/unbind/unit/knowledge` ⚠️写

**`all`**
- `GET` `/api/all/course`
- `GET` `/api/all/course/grades`
- `GET` `/api/all/teacher`

**`copy`**
- `GET` `/api/copy/listCourseInfo` ⚠️写
- `GET` `/api/copy/listGroupInfo` ⚠️写
- `GET` `/api/copy/unit` ⚠️写

**`copyLesson`**
- `GET` `/api/copyLesson` ⚠️写
- `GET` `/api/copyLesson/course` ⚠️写
- `GET` `/api/copyLesson/unit` ⚠️写

**`homeSchool`**
- `GET` `/api/homeSchool/courseOldTemplate`
- `GET` `/api/homeSchool/crossCourseArchive`
- `GET` `/api/homeSchool/listTemplateByCourseId`

**`courseResources`**
- `GET` `/api/courseResources/options`
- `GET` `/api/courseResources/teacher`

**`my`**
- `GET` `/api/my/courses`
- `GET` `/api/my/currentCourses`

**`qualityLesson`**
- `GET` `/api/qualityLesson`
- `POST` `/api/qualityLesson/addReflectionOrRecord` ⚠️写

**`quiz`**
- `POST` `/api/quiz/createOrUpdate` ⚠️写
- `POST` `/api/quiz/list`

**`relieve`**
- `GET` `/api/relieve/lesson/group`
- `GET` `/api/relieve/lesson/teacher`

**`acl`**
- `GET` `/api/acl/courseList`

**`add`**
- `POST` `/api/add/openLesson` ⚠️写

**`addCourseResources`**
- `GET` `/api/addCourseResources` ⚠️写

**`addQualityLesson`**
- `POST` `/api/addQualityLesson` ⚠️写

**`addResourcesFile`**
- `GET` `/api/addResourcesFile` ⚠️写

**`behaviorRecord`**
- `GET` `/calendar/api/behaviorRecord/listTeachers`

**`check`**
- `GET` `/api/check/lesson/type`

**`copyUnit`**
- `GET` `/api/copyUnit` ⚠️写

**`courseResourcesList`**
- `GET` `/api/courseResourcesList`

**`courseResourcesOverview`**
- `GET` `/api/courseResourcesOverview`

**`delete`**
- `GET` `/api/delete/openLesson` ⚠️写

**`deleteCourseResources`**
- `GET` `/api/deleteCourseResources` ⚠️写

**`deleteResourcesFile`**
- `GET` `/api/deleteResourcesFile` ⚠️写

**`deletedUnit`**
- `GET` `/api/deletedUnit` ⚠️写

**`examInfoList`**
- `POST` `/api/examInfoList`

**`exportUnitOrLesson`**
- `未知` `/api/exportUnitOrLesson` ⚠️写

**`getActivity`**
- `GET` `/api/getActivity/teachingSteps`

**`getAllTeachers`**
- `GET` `/api/getAllTeachers`

**`getAllTeachersByOrg`**
- `GET` `/api/getAllTeachersByOrg`

**`getChapterOfCourseId`**
- `GET` `/api/getChapterOfCourseId`

**`getCourseListByParams`**
- `GET` `/api/getCourseListByParams`

**`getCourseResources`**
- `GET` `/api/getCourseResources`

**`getDefaultTeachers`**
- `GET` `/api/getDefaultTeachers`

**`getLessonDetail`**
- `GET` `/api/getLessonDetail`

**`getLessonInfo`**
- `GET` `/api/getLessonInfo`

**`getQualityLesson`**
- `GET` `/api/getQualityLesson`

**`getStudentsBaseCourse`**
- `GET` `/api/getStudentsBaseCourse`

**`getTeachingOrg`**
- `GET` `/api/getTeachingOrg`

**`getUnitName`**
- `GET` `/api/getUnitName`

**`getUnitStudent`**
- `GET` `/api/getUnitStudent`

**`getUnitTeacher`**
- `GET` `/api/getUnitTeacher`

**`ifPurchaseCourseModule`**
- `GET` `/api/ifPurchaseCourseModule`

**`ifQualityLessonPermission`**
- `GET` `/api/ifQualityLessonPermission`

**`importUnitOrLesson`**
- `POST` `/api/importUnitOrLesson` ⚠️写

**`index`**
- `未知` `/work/api/index/getTeacher`

**`insertUnit`**
- `POST` `/api/insertUnit` ⚠️写

**`isCourseTeacher`**
- `GET` `/api/isCourseTeacher`

**`isDeletedUnit`**
- `GET` `/api/isDeletedUnit`

**`list`**
- `GET` `/api/list/lesson/teacher`

**`listActivityUnderUnitStudent`**
- `GET` `/api/listActivityUnderUnitStudent`

**`listActivityUnderUnitTeacher`**
- `GET` `/api/listActivityUnderUnitTeacher`

**`listAllOrgTeachers`**
- `GET` `/course/api/listAllOrgTeachers`

**`listCourseDetailOfStudent`**
- `GET` `/api/listCourseDetailOfStudent`

**`listCourseLessonByTeacher`**
- `GET` `/api/listCourseLessonByTeacher`

**`listGroupCourseName`**
- `GET` `/api/listGroupCourseName`

**`listGroupInfoByCourseId`**
- `GET` `/evaluation/api/listGroupInfoByCourseId`

**`listLessonByCourseIdAndUnitId`**
- `GET` `/api/listLessonByCourseIdAndUnitId`

**`listQualityLesson`**
- `GET` `/api/listQualityLesson`

**`listUnitUnderCourseResources`**
- `GET` `/api/listUnitUnderCourseResources`

**`listUnitUnderCourseStudent`**
- `GET` `/api/listUnitUnderCourseStudent`

**`listUnitUnderCourseTeacher`**
- `GET` `/api/listUnitUnderCourseTeacher`

**`moveLesson`**
- `GET` `/api/moveLesson` ⚠️写

**`prepareLessons`**
- `GET` `/api/prepareLessons/getThemeByType`

**`punctualitySubmissionRateOfCourse`**
- `GET` `/api/punctualitySubmissionRateOfCourse`

**`query`**
- `GET` `/calendar/api/query/currentCourseClassAttendanceEvents`

**`recipe`**
- `GET` `/iot/api/recipe/planWeek/byTeacher`

**`request`**
- `GET` `/api/request/openLesson`

**`reuseLesson`**
- `GET` `/api/reuseLesson`

**`reuseUnit`**
- `POST` `/api/reuseUnit`

**`save`**
- `POST` `/api/save/AI/prepareLessonData` ⚠️写

**`searchTeachingOrg`**
- `GET` `/api/searchTeachingOrg`

**`student`**
- `POST` `/api/student/listUnitUnderPageHome`

**`target`**
- `GET` `/api/target/activity/unit/list`

**`teach`**
- `GET` `/api/teach/getGradeListByCourseId`

**`teacherResetStuPassWord`**
- `GET` `/api/teacherResetStuPassWord`

**`teaching`**
- `GET` `/course/api/teaching/listUserAclConfig`

**`team`**
- `GET` `/api/team/listTeamByCourseId`

**`update`**
- `POST` `/api/update/openLesson` ⚠️写

**`updateCourseResources`**
- `GET` `/api/updateCourseResources` ⚠️写

**`updateQualityLesson`**
- `POST` `/api/updateQualityLesson` ⚠️写

**`updateResourcesLessonSort`**
- `GET` `/api/updateResourcesLessonSort` ⚠️写

**`updateResourcesUnitSort`**
- `GET` `/api/updateResourcesUnitSort` ⚠️写

**`updateUnit`**
- `POST` `/api/updateUnit` ⚠️写

**`updateUnitSort`**
- `GET` `/api/updateUnitSort` ⚠️写

### 评价与素养成绩（236）

**`power`**
- `POST` `/api/power/addOrUpdateExamPlan` ⚠️写
- `POST` `/api/power/addOrUpdateLevel` ⚠️写
- `POST` `/api/power/addOrUpdateNorm` ⚠️写
- `POST` `/api/power/addOrUpdateTemplate` ⚠️写
- `GET` `/api/power/deleteExamPlan` ⚠️写
- `GET` `/api/power/deleteLevel` ⚠️写
- `GET` `/api/power/deleteNorm` ⚠️写
- `GET` `/api/power/deleteTemplate` ⚠️写
- `GET` `/api/power/disableLevel` ⚠️写
- `GET` `/api/power/disableTemplate` ⚠️写
- `GET` `/api/power/download/template`
- `GET` `/api/power/examPlanById`
- `GET` `/api/power/examPlanList`
- `GET` `/api/power/export/student` ⚠️写
- `GET` `/api/power/exportErrorInfo` ⚠️写
- `GET` `/api/power/getGroupByGradeId`
- `GET` `/api/power/getPlanInfo`
- `GET` `/api/power/getStudentListByNormId`
- `GET` `/api/power/getStudentListByPlanId`
- `POST` `/api/power/import/studentScore` ⚠️写
- `GET` `/api/power/levelDetail`
- `GET` `/api/power/levelList`
- `GET` `/api/power/normCopyContent`
- `GET` `/api/power/normList`
- `GET` `/api/power/normList/byGradeId`
- `GET` `/api/power/overviewStatistics`
- `GET` `/api/power/planAnalysis`
- `GET` `/api/power/projectByGroup`
- `GET` `/api/power/projectList`
- `GET` `/api/power/reloadDataSource` ⚠️写
- `GET` `/api/power/stageList`
- `GET` `/api/power/studentDtail`
- `GET` `/api/power/studentList`
- `GET` `/api/power/templateDetail`
- `GET` `/api/power/templateList`
- `POST` `/api/power/upload/studentScore` ⚠️写
- `GET` `/evaluation/api/power/stageList`

**`user`**
- `GET` `/api/user/relation/lessonEvaluation`
- `POST` `/api/user/relation/lessonEvaluation/bindTemplate` ⚠️写
- `GET` `/api/user/relation/lessonEvaluation/context`
- `GET` `/api/user/relation/lessonEvaluation/mySubmission`
- `GET` `/api/user/relation/lessonEvaluation/reportExportData`
- `GET` `/api/user/relation/lessonEvaluation/resultDetails`
- `GET` `/api/user/relation/lessonEvaluation/resultOverview`
- `GET` `/api/user/relation/lessonEvaluation/templateOptions`
- `GET` `/api/user/relation/lessonEvaluation/templateOverview`
- `GET` `/api/user/relation/lessonEvaluation/templatePreview`
- `POST` `/api/user/relation/lessonEvaluation/updateVisibility` ⚠️写
- `GET` `/api/user/relation/lessonEvaluationTemplate`
- `POST` `/api/user/relation/lessonEvaluationTemplate/delete` ⚠️写
- `未知` `/api/user/relation/lessonEvaluationTemplate/detail`
- `未知` `/api/user/relation/lessonEvaluationTemplate/editorDetail` ⚠️写
- `POST` `/api/user/relation/lessonEvaluationTemplate/identityVisibility`
- `GET` `/api/user/relation/lessonEvaluationTemplate/identityVisibilityCapability`
- `POST` `/api/user/relation/lessonEvaluationTemplate/import` ⚠️写
- `POST` `/api/user/relation/lessonEvaluationTemplate/import/confirm` ⚠️写
- `未知` `/api/user/relation/lessonEvaluationTemplate/import/detail` ⚠️写
- `GET` `/api/user/relation/lessonEvaluationTemplate/list`
- `POST` `/api/user/relation/lessonEvaluationTemplate/parseDocx`
- `GET` `/api/user/relation/lessonEvaluationTemplate/permission`
- `POST` `/api/user/relation/lessonEvaluationTemplate/save` ⚠️写
- `POST` `/api/user/relation/lessonEvaluationTemplate/saveText` ⚠️写
- `POST` `/api/user/relation/lessonEvaluationTemplate/scoreVisibility`
- `POST` `/api/user/relation/lessonEvaluationTemplate/status`

**`evaluation`**
- `POST` `/evaluation/api/evaluation/addOrUpdateTemplate` ⚠️写
- `GET` `/evaluation/api/evaluation/copyTemplate` ⚠️写
- `GET` `/evaluation/api/evaluation/criterion/addCriterion` ⚠️写
- `GET` `/evaluation/api/evaluation/criterion/copyCriterionById` ⚠️写
- `GET` `/evaluation/api/evaluation/criterion/deleteCriterionById` ⚠️写
- `GET` `/evaluation/api/evaluation/criterion/getCriterionById`
- `GET` `/evaluation/api/evaluation/criterion/item/evaluationItemType`
- `GET` `/evaluation/api/evaluation/criterion/item/list`
- `GET` `/evaluation/api/evaluation/criterion/listCriterionByStatus`
- `GET` `/evaluation/api/evaluation/criterion/listEvaluationCriterion`
- `GET` `/evaluation/api/evaluation/criterion/listEvaluationCriterionByType`
- `GET` `/evaluation/api/evaluation/criterion/listExternalCriterion`
- `POST` `/evaluation/api/evaluation/criterion/updateCriterion` ⚠️写
- `GET` `/evaluation/api/evaluation/criterion/updateCriterionStatusById` ⚠️写
- `GET` `/evaluation/api/evaluation/deleteTemplate` ⚠️写
- `GET` `/evaluation/api/evaluation/getCourses`
- `GET` `/evaluation/api/evaluation/getTemplate`
- `GET` `/evaluation/api/evaluation/getTemplateByCourseIdAndSemesterId`
- `POST` `/evaluation/api/evaluation/importTemplate` ⚠️写
- `GET` `/evaluation/api/evaluation/listCourseByTemplateId`
- `POST` `/evaluation/api/evaluation/scheme/checkEvaluationSchemeData`
- `POST` `/evaluation/api/evaluation/scheme/copyEvaluationSchemeData` ⚠️写
- `GET` `/evaluation/api/evaluation/scheme/ifParentIndicator`
- `GET` `/evaluation/api/evaluation/scheme/ifViewPermissions`
- `GET` `/evaluation/api/evaluation/scheme/tableEvaluationSchemeIndicatorByStuId`
- `GET` `/evaluation/api/evaluation/templateList`

**`template`**
- `GET` `/api/template/addTemplateCourseRelation` ⚠️写
- `POST` `/api/template/batchAddTemplateRelation` ⚠️写
- `GET` `/api/template/checkAllowSettingTemplate`
- `GET` `/api/template/copyTemplate` ⚠️写
- `GET` `/api/template/deleteElementInfo` ⚠️写
- `GET` `/api/template/deleteTemplate` ⚠️写
- `GET` `/api/template/deletedTemplateCourseRelation` ⚠️写
- `GET` `/api/template/getAllElement`
- `GET` `/api/template/getCourses`
- `GET` `/api/template/getElementChildrenStructure`
- `GET` `/api/template/getElementRelation`
- `GET` `/api/template/getElementRelationByOrgId`
- `GET` `/api/template/getTemplateInfo`
- `GET` `/api/template/list`
- `GET` `/api/template/listForStage`
- `POST` `/api/template/saveElementChildrenStructure` ⚠️写
- `GET` `/api/template/subjectList`
- `GET` `/api/template/teachingOrgList`
- `GET` `/api/template/templateInfoList`
- `GET` `/api/template/templateList`
- `GET` `/api/template/updateElementSort` ⚠️写
- `POST` `/api/template/updateRelationInfo` ⚠️写
- `POST` `/api/template/updateTemplate` ⚠️写

**`indicator`**
- `GET` `/api/indicator/getIndicatorById`
- `GET` `/api/indicator/listEvidence`
- `GET` `/api/indicator/listIndicator`
- `GET` `/api/indicator/scale`
- `POST` `/evaluation/api/indicator/batchUpdateGrade` ⚠️写
- `POST` `/evaluation/api/indicator/batchUpdateSubject` ⚠️写
- `GET` `/evaluation/api/indicator/disableIndicatorTree` ⚠️写
- `GET` `/evaluation/api/indicator/exportIndicatorTreeByTypeCodeAndStage/errorData` ⚠️写
- `未知` `/evaluation/api/indicator/exportIndicatorTreeByTypeCodeAndStage/template` ⚠️写
- `GET` `/evaluation/api/indicator/findIndicatorTreeByBizTypeCode`
- `GET` `/evaluation/api/indicator/getGeneralLiteracyInitialData`
- `POST` `/evaluation/api/indicator/importIndicatorTreeByTypeCodeAndStage` ⚠️写
- `POST` `/evaluation/api/indicator/importIndicatorTreeByTypeCodeAndStage/calculateData` ⚠️写
- `GET` `/evaluation/api/indicator/listDescriptionByIndicatorIdAndTypeCode`
- `GET` `/evaluation/api/indicator/listIndicatorByGradeIdAndCourseId`
- `GET` `/evaluation/api/indicator/listIndicatorTreeByTypeCodeAndCourseId`
- `GET` `/evaluation/api/indicator/listIndicatorTreeByTypeCodeAndStage`
- `GET` `/evaluation/api/indicator/listItemDescriptionByIndicatorIdAndTypeCode`
- `GET` `/evaluation/api/indicator/listSubjectGroupByStage`
- `GET` `/evaluation/api/indicator/moveIndicatorTree` ⚠️写
- `POST` `/evaluation/api/indicator/saveGeneralLiteracyInitialData` ⚠️写
- `GET` `/evaluation/api/indicator/updateIndicatorTreeSort` ⚠️写

**`standardizedTest`**
- `未知` `/api/standardizedTest`
- `GET` `/api/standardizedTest/academicOverview`
- `GET` `/api/standardizedTest/courseScore`
- `GET` `/api/standardizedTest/deleteById` ⚠️写
- `GET` `/api/standardizedTest/evidenceList`
- `GET` `/api/standardizedTest/getLevelConfig`
- `GET` `/api/standardizedTest/getScoreLevel`
- `GET` `/api/standardizedTest/indicatorOverview`
- `GET` `/api/standardizedTest/listByStudent`
- `GET` `/api/standardizedTest/listIndicator`
- `GET` `/api/standardizedTest/numByStudent`
- `GET` `/api/standardizedTest/studentLevelList`

**`achievement`**
- `GET` `/api/achievement/auditStatistics` ⚠️写
- `GET` `/api/achievement/audit_list` ⚠️写
- `GET` `/api/achievement/result/growthRecord/count`
- `POST` `/api/achievement/resultWallFlow`
- `POST` `/api/achievement/result_wall`

**`gradeManagement`**
- `GET` `/api/gradeManagement/aclPermission`
- `未知` `/api/gradeManagement/exportEvaluationCategoryScore` ⚠️写
- `未知` `/api/gradeManagement/exportEvaluationItemScore` ⚠️写
- `GET` `/api/gradeManagement/listEvaluationCategoryScore`
- `GET` `/api/gradeManagement/listEvaluationItemScore`

**`teach`**
- `POST` `/api/teach/bind/indicator` ⚠️写
- `POST` `/api/teach/bind/unit/indicator` ⚠️写
- `GET` `/api/teach/get/indicator/list`
- `GET` `/api/teach/get/indicator/tree`
- `GET` `/api/teach/get/indicator/treeV2`

**`board`**
- `GET` `/api/board/evaluationPlanDataBoard`
- `GET` `/api/board/evaluationPlanList`
- `未知` `/api/board/export/evaluationPlanDataBoard` ⚠️写
- `GET` `/api/board/habitEvaluationPlanList`

**`determineReview`**
- `GET` `/api/determineReview/delete` ⚠️写
- `GET` `/api/determineReview/myUploadData`
- `GET` `/api/determineReview/studentAssessmentData`
- `POST` `/api/determineReview/uploadStudentEvaluationResults` ⚠️写

**`elementResult`**
- `POST` `/api/elementResult/add` ⚠️写
- `POST` `/api/elementResult/forcedLock`
- `POST` `/api/elementResult/getLock`
- `POST` `/api/elementResult/releaseLock`

**`export`**
- `GET` `/api/export/achievement/result/wall/byId` ⚠️写
- `GET` `/api/export/achievement/result/whiteList` ⚠️写
- `未知` `/evaluation/api/export/listEvaluationProgressByAllSubject` ⚠️写
- `未知` `/evaluation/api/export/listEvaluationProgressBySubject` ⚠️写

**`statistics`**
- `POST` `/calendar/api/statistics/behaviorSummary/indicator/detail/batch` ⚠️写
- `GET` `/calendar/api/statistics/listStudentScore`
- `GET` `/calendar/api/statistics/teacher/listScoreDetail`

**`courseEvaluation`**
- `POST` `/evaluation/api/courseEvaluation/getIntelligenceParameterByParams`
- `GET` `/evaluation/api/courseEvaluation/getIntelligenceResult`

**`achievementOperation`**
- `GET` `/api/achievementOperation`

**`addGraduationCriteria`**
- `POST` `/api/addGraduationCriteria` ⚠️写

**`addOrUpdateCourseEstimatedScore`**
- `POST` `/evaluation/api/addOrUpdateCourseEstimatedScore` ⚠️写

**`addOrUpdateCourseGpa`**
- `POST` `/evaluation/api/addOrUpdateCourseGpa` ⚠️写

**`behaviorEntry`**
- `GET` `/calendar/api/behaviorEntry/indicators`

**`behaviorSku`**
- `GET` `/calendar/api/behaviorSku/getStudentScore`

**`comprehensivePerformance`**
- `GET` `/api/comprehensivePerformance`

**`copyGraduationCriteria`**
- `GET` `/api/copyGraduationCriteria` ⚠️写

**`deleteCourseEstimatedScore`**
- `GET` `/evaluation/api/deleteCourseEstimatedScore` ⚠️写

**`deleteGraduationCriteria`**
- `GET` `/api/deleteGraduationCriteria` ⚠️写

**`disableGraduationCriteria`**
- `GET` `/api/disableGraduationCriteria` ⚠️写

**`estimatedScorePermission`**
- `GET` `/evaluation/api/estimatedScorePermission`

**`evaluationCriterionPermission`**
- `GET` `/evaluation/api/evaluationCriterionPermission`

**`evaluationProgress`**
- `GET` `/api/evaluationProgress/aclPermission`

**`evaluationTemplatePermission`**
- `GET` `/evaluation/api/evaluationTemplatePermission`

**`exportListAutonomyEvaluation`**
- `未知` `/api/exportListAutonomyEvaluation` ⚠️写

**`exportListCourseScoreManager`**
- `未知` `/api/exportListCourseScoreManager` ⚠️写

**`getCourseEstimatedScore`**
- `GET` `/evaluation/api/getCourseEstimatedScore`

**`getCourseGpaByStage`**
- `GET` `/evaluation/api/getCourseGpaByStage`

**`getCreditSetting`**
- `GET` `/api/getCreditSetting`

**`getCreditSettingList`**
- `GET` `/api/getCreditSettingList`

**`getDetailAchievement`**
- `GET` `/api/getDetailAchievement`

**`getEvaluationProgressByCourseId`**
- `GET` `/evaluation/api/getEvaluationProgressByCourseId`

**`getEvaluationProgressByGroupId`**
- `GET` `/evaluation/api/getEvaluationProgressByGroupId`

**`getGraduationCriteria`**
- `GET` `/api/getGraduationCriteria`

**`getLockScoreTemplate`**
- `GET` `/evaluation/api/getLockScoreTemplate`

**`gpaSettingPermission`**
- `GET` `/evaluation/api/gpaSettingPermission`

**`growthAim`**
- `未知` `/api/growthAim/export/achievementAnalysis` ⚠️写

**`homeSchool`**
- `GET` `/api/homeSchool/evaluationTag`

**`ifLockScore`**
- `GET` `/evaluation/api/ifLockScore`

**`indicatorTreePermission`**
- `GET` `/evaluation/api/indicatorTreePermission`

**`listAchievement`**
- `GET` `/api/listAchievement/fileList`

**`listAutonomyEvaluation`**
- `GET` `/api/listAutonomyEvaluation`

**`listAutonomyEvaluationEnumeration`**
- `GET` `/api/listAutonomyEvaluationEnumeration`

**`listCourseAndScoreBySemId`**
- `GET` `/api/listCourseAndScoreBySemId`

**`listCourseByGpaId`**
- `GET` `/evaluation/api/listCourseByGpaId`

**`listCourseScoreLog`**
- `GET` `/api/listCourseScoreLog`

**`listCourseScoreManager`**
- `GET` `/api/listCourseScoreManager`

**`listEvaluationProgressByAllSubject`**
- `GET` `/evaluation/api/listEvaluationProgressByAllSubject`

**`listEvaluationProgressBySubject`**
- `GET` `/evaluation/api/listEvaluationProgressBySubject`

**`listEvaluationScoreByStuId`**
- `GET` `/api/listEvaluationScoreByStuId`

**`listGraduationCriteria`**
- `GET` `/api/listGraduationCriteria`

**`listModuleContentOfScoreDetail`**
- `GET` `/api/listModuleContentOfScoreDetail`

**`listModuleContentOfScoreManager`**
- `GET` `/api/listModuleContentOfScoreManager`

**`newBehaviorRecord`**
- `POST` `/calendar/api/newBehaviorRecord/studentScoreList`

**`selectCourseEvaluationStudentInfo`**
- `GET` `/evaluation/api/selectCourseEvaluationStudentInfo`

**`studentInfoAndCourseScore`**
- `GET` `/api/studentInfoAndCourseScore`

**`teacher`**
- `POST` `/api/teacher/getAchievementDetail`

**`updateAchievementAndSendMessage`**
- `POST` `/api/updateAchievementAndSendMessage` ⚠️写

**`updateAutonomyEvaluation`**
- `GET` `/api/updateAutonomyEvaluation` ⚠️写

**`updateCourseScore`**
- `POST` `/api/updateCourseScore` ⚠️写

**`updateCourseScoreV2`**
- `POST` `/api/updateCourseScoreV2` ⚠️写

**`updateGraduationCriteria`**
- `POST` `/api/updateGraduationCriteria` ⚠️写

### 家校与反馈（147）

**`homeSchool`**
- `GET` `/api/homeSchool`
- `GET` `/api/homeSchool/cardDetailById`
- `GET` `/api/homeSchool/columnList`
- `未知` `/api/homeSchool/exportTableData` ⚠️写
- `POST` `/api/homeSchool/exportTableView` ⚠️写
- `GET` `/api/homeSchool/exportTableViewOld` ⚠️写
- `GET` `/api/homeSchool/fillTemplate`
- `GET` `/api/homeSchool/getSchoolRoleList`
- `GET` `/api/homeSchool/insertTypeWork` ⚠️写
- `GET` `/api/homeSchool/linkList`
- `GET` `/api/homeSchool/mentionData`
- `GET` `/api/homeSchool/moduleDetailById`
- `GET` `/api/homeSchool/moduleList`
- `GET` `/api/homeSchool/newTemplates`
- `GET` `/api/homeSchool/personInfoByStudent`
- `GET` `/api/homeSchool/selectTemplateList`
- `GET` `/api/homeSchool/shareSetting`
- `GET` `/api/homeSchool/stageBySchool`
- `GET` `/api/homeSchool/tableColumns`
- `POST` `/api/homeSchool/tableData`
- `POST` `/api/homeSchool/tableView`
- `GET` `/api/homeSchool/templateBaseDetail`
- `POST` `/api/homeSchool/templateBaseUpdate`
- `GET` `/api/homeSchool/templateContentDetail`
- `POST` `/api/homeSchool/templateContentUpdate`
- `GET` `/api/homeSchool/templateCopy`
- `GET` `/api/homeSchool/templateDelete`
- `GET` `/api/homeSchool/templateList`
- `GET` `/api/homeSchool/templateReview`
- `GET` `/api/homeSchool/templateStatusUpdate`
- `GET` `/api/homeSchool/typeWorkByStudent`
- `GET` `/api/homeSchool/typeWorkList`
- `POST` `/api/homeSchool/updateOrInsertShare` ⚠️写

**`feedback`**
- `GET` `/api/feedback/auditFeedbackDetail` ⚠️写
- `GET` `/api/feedback/checkCreatePlanAuthority`
- `GET` `/api/feedback/deleteById` ⚠️写
- `未知` `/api/feedback/download/template`
- `GET` `/api/feedback/getNotificationReceiver`
- `GET` `/api/feedback/gradeByStage`
- `GET` `/api/feedback/gradeList`
- `GET` `/api/feedback/groupByGrade`
- `GET` `/api/feedback/groupList`
- `POST` `/api/feedback/importData` ⚠️写
- `POST` `/api/feedback/importNum` ⚠️写
- `POST` `/api/feedback/insertDownloadWeekFeedbackPdfJob` ⚠️写
- `GET` `/api/feedback/listDownloadWeekFeedbackPdfJob`
- `GET` `/api/feedback/moduleList`
- `GET` `/api/feedback/parent/planWeek`
- `GET` `/api/feedback/parent/planWeekDetail`
- `GET` `/api/feedback/planById`
- `GET` `/api/feedback/planContentList`
- `POST` `/api/feedback/planCreateOrUpdate`
- `GET` `/api/feedback/planList`
- `GET` `/api/feedback/planWeekMonth`
- `GET` `/api/feedback/rollbackAuditFeedbackDetail`
- `GET` `/api/feedback/sendMessageByPlanIdAndTime` ⚠️写
- `GET` `/api/feedback/stageBySchool`
- `GET` `/api/feedback/studentByGroup`
- `GET` `/api/feedback/updatePublicStatus` ⚠️写

**`recipe`**
- `POST` `/iot/api/recipe/addOrUpdatePlan` ⚠️写
- `POST` `/iot/api/recipe/addOrUpdateWeekPlan` ⚠️写
- `GET` `/iot/api/recipe/batchDeletePlan` ⚠️写
- `GET` `/iot/api/recipe/deletePlan` ⚠️写
- `GET` `/iot/api/recipe/deleteWeekPlan` ⚠️写
- `GET` `/iot/api/recipe/detailByPlanId`
- `GET` `/iot/api/recipe/detailByWeekPlanId`
- `GET` `/iot/api/recipe/messageSendObject`
- `GET` `/iot/api/recipe/messageSendStart`
- `GET` `/iot/api/recipe/messageSendType`
- `GET` `/iot/api/recipe/permissionList`
- `GET` `/iot/api/recipe/planAllWeek`
- `GET` `/iot/api/recipe/planList`
- `GET` `/iot/api/recipe/planWeek/parent`
- `GET` `/iot/api/recipe/schoolDoctorStatus`
- `GET` `/iot/api/recipe/stageBySchool`
- `GET` `/iot/api/recipe/updateDisableStatus` ⚠️写
- `GET` `/iot/api/recipe/weekDetail/parent`
- `GET` `/iot/api/recipe/weekPlanList`
- `GET` `/iot/api/recipe/weekPlanTitleList`

**`statistics`**
- `未知` `/api/statistics/grade/group/analyze/rank/export` ⚠️写
- `POST` `/calendar/api/statistics/class/group/analyze/rank`
- `POST` `/calendar/api/statistics/grade/group/analyze/rank`
- `未知` `/calendar/api/statistics/grade/group/manual/detail`
- `GET` `/calendar/api/statistics/group/analyze`
- `POST` `/calendar/api/statistics/group/analyze/overview`
- `POST` `/calendar/api/statistics/group/analyzeJSONExplain`
- `GET` `/calendar/api/statistics/group/chiefTutor`
- `GET` `/calendar/api/statistics/group/dayAnalyze`
- `POST` `/calendar/api/statistics/group/student/count`
- `GET` `/calendar/api/statistics/listTutorStudent`
- `GET` `/calendar/api/statistics/stu/tutor`
- `POST` `/calendar/api/statistics/tutor/analyze/overview`
- `POST` `/calendar/api/statistics/tutor/student/analyze/rank`

**`student`**
- `GET` `/api/student/daily/countStudentDaily`
- `GET` `/api/student/daily/dict/allListDailyDict`
- `GET` `/api/student/daily/dict/listDailyDict`
- `POST` `/api/student/daily/finishedStudentDailyInfo`
- `GET` `/api/student/daily/getSchoolDailyConfig`
- `GET` `/api/student/daily/getSchoolDailyConfigNew`
- `GET` `/api/student/daily/listGroup`
- `GET` `/api/student/daily/listStudentInfo`
- `POST` `/api/student/daily/updateStudentDailyInfo` ⚠️写
- `GET` `/course/api/student/roster/listGroup`
- `GET` `/course/api/student/roster/listGroupByTag`
- `GET` `/course/api/student/roster/listStageGradeGroup`

**`team`**
- `POST` `/api/team/createTeam` ⚠️写
- `GET` `/api/team/deletedBigGroup` ⚠️写
- `GET` `/api/team/disbandTeam`
- `GET` `/api/team/getBigGroupList`
- `GET` `/api/team/groupInfoList`
- `GET` `/api/team/info`
- `GET` `/api/team/members`
- `GET` `/api/team/newMembers`
- `POST` `/api/team/saveGroupTeam` ⚠️写
- `GET` `/api/team/updateBigGroup` ⚠️写
- `POST` `/api/team/updateTeam` ⚠️写

**`home-school`**
- `GET` `/api/home-school`
- `GET` `/api/home-school/new-version-gray`
- `未知` `/api/home-school/templates/`

**`new`**
- `GET` `/api/new/getStudentGroupList/pc`
- `GET` `/api/new/getStudentGroupList/pcConfig`
- `GET` `/api/new/group/list/pc`

**`stageFeedback`**
- `GET` `/evaluation/api/stageFeedback/aiFeedbackData`
- `GET` `/evaluation/api/stageFeedback/getAIFeedbackParam`
- `POST` `/evaluation/api/stageFeedback/saveAIFeedbackData` ⚠️写

**`board`**
- `GET` `/api/board/groupList`
- `未知` `/api/board/groupListReport`

**`group`**
- `GET` `/api/group/newStudents`
- `GET` `/api/group/students`

**`studentManagement`**
- `POST` `/calendar/api/studentManagement/group`
- `POST` `/calendar/api/studentManagement/my/group`

**`(root)`**
- `GET` `/api//selectAllTutor`

**`export`**
- `未知` `/api/export/feedbackList` ⚠️写

**`exportSummary`**
- `GET` `/calendar/api/exportSummary` ⚠️写

**`getGroupByGradeId`**
- `GET` `/api/getGroupByGradeId`

**`getTutorSchoolConfig`**
- `GET` `/api/getTutorSchoolConfig`

**`gradeSummary`**
- `GET` `/calendar/api/gradeSummary`

**`groupSummary`**
- `GET` `/calendar/api/groupSummary`

**`groupSummaryDetail`**
- `GET` `/calendar/api/groupSummaryDetail`

**`ifTutorSchoolConfig`**
- `GET` `/api/ifTutorSchoolConfig`

**`listGroup`**
- `POST` `/api/listGroup`

**`saveTutorSchoolConfig`**
- `POST` `/api/saveTutorSchoolConfig` ⚠️写

**`selectAllTutor`**
- `GET` `/api/selectAllTutor`

**`selectGroupInfo`**
- `GET` `/evaluation/api/selectGroupInfo`

**`selectGroupInfoByPlanId`**
- `GET` `/evaluation/api/selectGroupInfoByPlanId`

**`stageSummary`**
- `GET` `/calendar/api/stageSummary`

**`stage_feedback_list`**
- `POST` `/evaluation/api/stage_feedback_list`

### 学生行为与德育（140）

**`newBehaviorRecord`**
- `GET` `/calendar/api/newBehaviorRecord`
- `GET` `/calendar/api/newBehaviorRecord/appeal`
- `POST` `/calendar/api/newBehaviorRecord/batchUpdate` ⚠️写
- `POST` `/calendar/api/newBehaviorRecord/batchUpdateEvaluatorDetail` ⚠️写
- `GET` `/calendar/api/newBehaviorRecord/behavior/calculation/list`
- `未知` `/calendar/api/newBehaviorRecord/behavior/export` ⚠️写
- `未知` `/calendar/api/newBehaviorRecord/behavior/grade`
- `POST` `/calendar/api/newBehaviorRecord/behavior/group`
- `POST` `/calendar/api/newBehaviorRecord/behavior/import/v2` ⚠️写
- `POST` `/calendar/api/newBehaviorRecord/behavior/my/group`
- `GET` `/calendar/api/newBehaviorRecord/behavior/permission`
- `GET` `/calendar/api/newBehaviorRecord/behavior/stage`
- `GET` `/calendar/api/newBehaviorRecord/buildingArea`
- `GET` `/calendar/api/newBehaviorRecord/checkConfigPermission`
- `GET` `/calendar/api/newBehaviorRecord/checkStageConfigPermission`
- `POST` `/calendar/api/newBehaviorRecord/commitGroupRecord` ⚠️写
- `GET` `/calendar/api/newBehaviorRecord/deleteBehaviorRecord` ⚠️写
- `GET` `/calendar/api/newBehaviorRecord/deleteDetail` ⚠️写
- `GET` `/calendar/api/newBehaviorRecord/earlyWarning/actionList`
- `GET` `/calendar/api/newBehaviorRecord/earlyWarning/detail`
- `GET` `/calendar/api/newBehaviorRecord/earlyWarning/enable` ⚠️写
- `POST` `/calendar/api/newBehaviorRecord/earlyWarning/followRecord/add` ⚠️写
- `GET` `/calendar/api/newBehaviorRecord/earlyWarning/followRecord/delete` ⚠️写
- `POST` `/calendar/api/newBehaviorRecord/earlyWarning/followRecord/update` ⚠️写
- `POST` `/calendar/api/newBehaviorRecord/earlyWarning/grade/analysis`
- `POST` `/calendar/api/newBehaviorRecord/earlyWarning/group/analysis`
- `GET` `/calendar/api/newBehaviorRecord/earlyWarning/levelList`
- `GET` `/calendar/api/newBehaviorRecord/earlyWarning/list`
- `POST` `/calendar/api/newBehaviorRecord/earlyWarning/manualCreate`
- `GET` `/calendar/api/newBehaviorRecord/earlyWarning/rule/enable` ⚠️写
- `POST` `/calendar/api/newBehaviorRecord/earlyWarning/saveOrUpdate` ⚠️写
- `GET` `/calendar/api/newBehaviorRecord/earlyWarning/sendMessage` ⚠️写
- `POST` `/calendar/api/newBehaviorRecord/earlyWarning/student/analysis`
- `GET` `/calendar/api/newBehaviorRecord/floor`
- `GET` `/calendar/api/newBehaviorRecord/getAllBadge`
- `GET` `/calendar/api/newBehaviorRecord/groupOverview`
- `POST` `/calendar/api/newBehaviorRecord/groupStudent`
- `GET` `/calendar/api/newBehaviorRecord/listBadge`
- `GET` `/calendar/api/newBehaviorRecord/listBehavior`
- `GET` `/calendar/api/newBehaviorRecord/listBehaviorAllUseType`
- `GET` `/calendar/api/newBehaviorRecord/listBehaviorByMode`
- `GET` `/calendar/api/newBehaviorRecord/listBehaviorTree`
- `GET` `/calendar/api/newBehaviorRecord/listDorm`
- `GET` `/calendar/api/newBehaviorRecord/listDormInfo`
- `POST` `/calendar/api/newBehaviorRecord/listGroupRecord`
- `POST` `/calendar/api/newBehaviorRecord/listStudent`
- `GET` `/calendar/api/newBehaviorRecord/listStudentBadge`
- `GET` `/calendar/api/newBehaviorRecord/listTag`
- `GET` `/calendar/api/newBehaviorRecord/revokeTier` ⚠️写
- `POST` `/calendar/api/newBehaviorRecord/saveOrUpdateGroupRecord` ⚠️写
- `POST` `/calendar/api/newBehaviorRecord/studentBehaviorDetail`
- `GET` `/calendar/api/newBehaviorRecord/studentTierDetail`
- `POST` `/calendar/api/newBehaviorRecord/updateBadgeConfig` ⚠️写
- `POST` `/calendar/api/newBehaviorRecord/updateConfig` ⚠️写
- `POST` `/calendar/api/newBehaviorRecord/updateRecord` ⚠️写
- `POST` `/calendar/api/newBehaviorRecord/write/group` ⚠️写

**`behaviorRecord`**
- `GET` `/calendar/api/behaviorRecord`
- `未知` `/calendar/api/behaviorRecord/aiAssistant`
- `未知` `/calendar/api/behaviorRecord/allStu/behavior/download/template`
- `未知` `/calendar/api/behaviorRecord/allStu/behavior/downloadFailData`
- `POST` `/calendar/api/behaviorRecord/allStu/behavior/import` ⚠️写
- `POST` `/calendar/api/behaviorRecord/allStu/behavior/importCount` ⚠️写
- `POST` `/calendar/api/behaviorRecord/approval`
- `GET` `/calendar/api/behaviorRecord/approval/detail`
- `POST` `/calendar/api/behaviorRecord/create` ⚠️写
- `POST` `/calendar/api/behaviorRecord/editRecord` ⚠️写
- `GET` `/calendar/api/behaviorRecord/getOwnChildrenInfo`
- `GET` `/calendar/api/behaviorRecord/getUserSubject`
- `GET` `/calendar/api/behaviorRecord/groupAnalyze`
- `未知` `/calendar/api/behaviorRecord/groupAnalyze/export` ⚠️写
- `POST` `/calendar/api/behaviorRecord/groupStatistics`
- `GET` `/calendar/api/behaviorRecord/listBehaviorType`
- `GET` `/calendar/api/behaviorRecord/listDorms`
- `GET` `/calendar/api/behaviorRecord/listGrades`
- `POST` `/calendar/api/behaviorRecord/listStudentRecord`
- `GET` `/calendar/api/behaviorRecord/listStudents`
- `GET` `/calendar/api/behaviorRecord/listSubjectByStage`
- `POST` `/calendar/api/behaviorRecord/pendingReview/list`
- `POST` `/calendar/api/behaviorRecord/saveOrUpdatePunishment` ⚠️写
- `POST` `/calendar/api/behaviorRecord/showBehaviorRecordDetail`
- `POST` `/calendar/api/behaviorRecord/showLatestRecord`
- `POST` `/calendar/api/behaviorRecord/showMyPending`
- `POST` `/calendar/api/behaviorRecord/showTypeStatistics`
- `POST` `/calendar/api/behaviorRecord/update` ⚠️写

**`statistics`**
- `POST` `/calendar/api/statistics/allStu/behavior`
- `GET` `/calendar/api/statistics/allStu/behavior/export` ⚠️写
- `GET` `/calendar/api/statistics/behavior`
- `GET` `/calendar/api/statistics/behavior/punishment/detail`
- `POST` `/calendar/api/statistics/behaviorSummary/export/data` ⚠️写
- `POST` `/calendar/api/statistics/behaviorSummary/record/batch` ⚠️写
- `POST` `/calendar/api/statistics/behaviorSummary/record/page`
- `POST` `/calendar/api/statistics/distributionChartDetails/activeBehavior`
- `POST` `/calendar/api/statistics/dorm/allStu/behavior`
- `POST` `/calendar/api/statistics/dorm/analyze/allStu/behavior`
- `POST` `/calendar/api/statistics/dorm/analyze/overview`
- `POST` `/calendar/api/statistics/dorm/analyze/rank`
- `POST` `/calendar/api/statistics/dorm/analyze/student/rank`
- `GET` `/calendar/api/statistics/dorm/behavior`
- `GET` `/calendar/api/statistics/group/behaviorAnalyze`
- `GET` `/calendar/api/statistics/stu/behaviorAnalyze`

**`classBehaviorRecord`**
- `GET` `/calendar/api/classBehaviorRecord`
- `POST` `/calendar/api/classBehaviorRecord/allStu/behavior`
- `未知` `/calendar/api/classBehaviorRecord/allStu/behavior/export` ⚠️写
- `GET` `/calendar/api/classBehaviorRecord/approval/detail`
- `未知` `/calendar/api/classBehaviorRecord/behavior/grade`
- `POST` `/calendar/api/classBehaviorRecord/create` ⚠️写
- `GET` `/calendar/api/classBehaviorRecord/listBehavior`
- `POST` `/calendar/api/classBehaviorRecord/student/write/group` ⚠️写

**`dormitoryBehavior`**
- `GET` `/calendar/api/dormitoryBehavior/records/batch` ⚠️写
- `GET` `/calendar/api/dormitoryBehavior/reports/dorms`
- `GET` `/calendar/api/dormitoryBehavior/reports/students`
- `GET` `/calendar/api/dormitoryBehavior/students/add-options`
- `GET` `/calendar/api/dormitoryBehavior/students/context`
- `GET` `/calendar/api/dormitoryBehavior/students/dorms`
- `GET` `/calendar/api/dormitoryBehavior/students/page`
- `GET` `/calendar/api/dormitoryBehavior/students/selection-summary`

**`behaviorSku`**
- `POST` `/calendar/api/behaviorSku/addSku` ⚠️写
- `POST` `/calendar/api/behaviorSku/addSkuExchange` ⚠️写
- `GET` `/calendar/api/behaviorSku/listSku`
- `GET` `/calendar/api/behaviorSku/listSkuExchange`
- `POST` `/calendar/api/behaviorSku/updateSku` ⚠️写
- `POST` `/calendar/api/behaviorSku/verifySku` ⚠️写

**`rank`**
- `GET` `/calendar/api/rank/getLastUploadFieldUrl`
- `GET` `/calendar/api/rank/getSchoolConfig`
- `GET` `/calendar/api/rank/listRelatedBehavior`
- `POST` `/calendar/api/rank/saveOrUpdateRelatedBehavior` ⚠️写
- `POST` `/calendar/api/rank/saveOrUpdateSchoolConfig` ⚠️写

**`classBehavior`**
- `GET` `/calendar/api/classBehavior`
- `未知` `/calendar/api/classBehavior/report/`
- `未知` `/calendar/api/classBehavior/report/export/jobs/` ⚠️写
- `POST` `/calendar/api/classBehavior/report/export/v2/jobs` ⚠️写

**`studentBehavior`**
- `未知` `/api/studentBehavior/analysis/export` ⚠️写
- `GET` `/calendar/api/studentBehavior`
- `未知` `/calendar/api/studentBehavior/analysis/`

**`behaviorType`**
- `GET` `/calendar/api/behaviorType/list`

**`listDormPermission`**
- `GET` `/calendar/api/listDormPermission`

**`moralEduStatistics`**
- `GET` `/api/moralEduStatistics/CIOMetric`

**`school`**
- `GET` `/calendar/api/school/getDormStage`

**`setStudentDormStatus`**
- `POST` `/calendar/api/setStudentDormStatus` ⚠️写

**`studentManagement`**
- `GET` `/calendar/api/studentManagement/dorms`

### 任务与作业（138）

**`capture`**
- `GET` `/api/capture`
- `POST` `/api/capture/addCaptureLabelRelation` ⚠️写
- `POST` `/api/capture/addRegularLabel` ⚠️写
- `POST` `/api/capture/addTypeWorkCaptureRelation` ⚠️写
- `POST` `/api/capture/auditCapture` ⚠️写
- `GET` `/api/capture/deleteCaptureById` ⚠️写
- `GET` `/api/capture/findResultWallByCaptureId`
- `GET` `/api/capture/findTreeView`
- `POST` `/api/capture/findUserCaptureCount`
- `POST` `/api/capture/findUserCaptureCountConfig`
- `GET` `/api/capture/getCaptureByCaptureId`
- `GET` `/api/capture/getCaptureByCaptureId/report/data`
- `GET` `/api/capture/getCapturerStudens`
- `GET` `/api/capture/getRegularLabel`
- `GET` `/api/capture/getTutorStudentList`
- `GET` `/api/capture/getTypeWork`
- `GET` `/api/capture/getUploadPhotoPermission`
- `POST` `/api/capture/insertBatchItemResult` ⚠️写
- `POST` `/api/capture/insertBatchItemResultAndRelease` ⚠️写
- `GET` `/api/capture/markHighlightMoment`
- `POST` `/api/capture/removeCaptureLabelRelation` ⚠️写
- `POST` `/api/capture/removeTypeWorkCaptureRelation` ⚠️写
- `GET` `/api/capture/selectAllRegularLabel`
- `GET` `/api/capture/selectCaptureByCaptureId`
- `GET` `/api/capture/selectEvaluationCategoryByExample`
- `GET` `/api/capture/selectEvaluationItem`
- `GET` `/api/capture/selectMarkAllCaptureLabel`
- `GET` `/api/capture/selectMarkAllTypeWork`
- `POST` `/api/capture/submitCapture` ⚠️写
- `GET` `/api/capture/typeWorkList`
- `POST` `/api/capture/updateCapture` ⚠️写

**`learn`**
- `POST` `/api/learn/batch/createResourcePublish` ⚠️写
- `POST` `/api/learn/batchSave/teachingSteps` ⚠️写
- `GET` `/api/learn/check/copy/group` ⚠️写
- `GET` `/api/learn/check/copy/lesson` ⚠️写
- `POST` `/api/learn/copy/resource` ⚠️写
- `POST` `/api/learn/createLearnList` ⚠️写
- `POST` `/api/learn/createResourcePublish` ⚠️写
- `GET` `/api/learn/deleteLearnListResource` ⚠️写
- `GET` `/api/learn/getTaskDetails`
- `POST` `/api/learn/listLearnListSort`
- `POST` `/api/learn/listLearnListStudent`
- `POST` `/api/learn/listLearnListTeacher`
- `POST` `/api/learn/resource/create` ⚠️写
- `POST` `/api/learn/save/teachingSteps` ⚠️写
- `GET` `/api/learn/selected/object`
- `GET` `/api/learn/taskResult/checkLock`
- `POST` `/api/learn/taskResult/forcedLock`
- `POST` `/api/learn/taskResult/releaseLock`
- `POST` `/api/learn/teachingSteps/checkLock`
- `GET` `/api/learn/teachingSteps/forcedBatchLock`
- `POST` `/api/learn/teachingSteps/getBatchLock`
- `POST` `/api/learn/teachingSteps/getLock`
- `POST` `/api/learn/teachingSteps/releaseBatchLock`
- `GET` `/api/learn/updateExpectTime` ⚠️写
- `POST` `/api/learn/updateLearnListResource` ⚠️写
- `POST` `/api/learn/updateResourcePublish` ⚠️写

**`homeworkManagement`**
- `GET` `/api/homeworkManagement/export` ⚠️写
- `GET` `/api/homeworkManagement/matrix`
- `PUT` `/api/homeworkManagement/offline`
- `POST` `/api/homeworkManagement/offline/copy` ⚠️写
- `POST` `/api/homeworkManagement/offline/delete` ⚠️写
- `GET` `/api/homeworkManagement/offline/detail`
- `GET` `/api/homeworkManagement/offline/options`
- `POST` `/api/homeworkManagement/offline/students`
- `POST` `/api/homeworkManagement/offline/students/remove` ⚠️写
- `POST` `/api/homeworkManagement/rosters/batch` ⚠️写
- `PUT` `/api/homeworkManagement/schedule`
- `POST` `/api/homeworkManagement/statistics`
- `POST` `/api/homeworkManagement/status`
- `POST` `/api/homeworkManagement/status/batch` ⚠️写
- `POST` `/api/homeworkManagement/status/batch/preview` ⚠️写
- `GET` `/api/homeworkManagement/status/options`
- `PUT` `/api/homeworkManagement/title`

**`draft`**
- `GET` `/api/draft`
- `GET` `/api/draft/allSimpleDraft`
- `POST` `/api/draft/autoSubmitDraft`
- `GET` `/api/draft/deleteDraft` ⚠️写
- `GET` `/api/draft/detailDraft`
- `POST` `/api/draft/submitDraft` ⚠️写

**`taskPublish`**
- `GET` `/api/taskPublish/data/statistics`
- `GET` `/api/taskPublish/findDescriptionListByIndicatorId`
- `GET` `/api/taskPublish/findIndicatorTree`
- `GET` `/api/taskPublish/getIndicatorTreeByTaskId`
- `GET` `/api/taskPublish/getTaskCountForStudent`

**`task`**
- `GET` `/api/task/evaluation/criterion/list`
- `GET` `/api/task/getEvaluationItemListByCategoryId`
- `GET` `/api/task/my/courses`
- `GET` `/api/task/unit/list`

**`user`**
- `GET` `/api/user/relation/checkPublishDiagnosticLessonPermission`
- `POST` `/api/user/relation/lessonEvaluation/saveDraft` ⚠️写
- `POST` `/api/user/relation/lessonEvaluation/submit` ⚠️写
- `GET` `/api/user/relation/updateTaskUserRelationLesson` ⚠️写

**`file-services`**
- `GET` `/center/api/file-services/addFileAnalysisTask` ⚠️写
- `GET` `/center/api/file-services/addJsonPdfTask` ⚠️写
- `未知` `/center/api/file-services/getJsonPdfTask`

**`leaveFlow`**
- `POST` `/leave/api/leaveFlow/config/publish` ⚠️写
- `POST` `/leave/api/leaveFlow/config/saveDraft` ⚠️写

**`new`**
- `POST` `/api/new/getTaskResultList`
- `POST` `/api/new/getTaskUser`

**`users`**
- `POST` `/api/users/taskPublish/hurry` ⚠️写
- `POST` `/api/users/taskPublish/status`

**`course`**
- `GET` `/api/course/taskPublishs`

**`createNewPublish`**
- `POST` `/api/createNewPublish` ⚠️写

**`createNewTask`**
- `POST` `/api/createNewTask` ⚠️写

**`deleteTask`**
- `GET` `/api/deleteTask` ⚠️写

**`deleteTaskPublish`**
- `GET` `/api/deleteTaskPublish` ⚠️写

**`endTaskPublish`**
- `GET` `/api/endTaskPublish`

**`exportCourseTaskStatisticsByParams`**
- `GET` `/api/exportCourseTaskStatisticsByParams` ⚠️写

**`exportStudentTaskStatisticsByParams`**
- `GET` `/api/exportStudentTaskStatisticsByParams` ⚠️写

**`exportTaskStatisticsByParams`**
- `GET` `/api/exportTaskStatisticsByParams` ⚠️写

**`get`**
- `未知` `/api/get/taskFileList`

**`getAllTasks`**
- `GET` `/api/getAllTasks`

**`getCourseTaskStatisticsByParams`**
- `GET` `/api/getCourseTaskStatisticsByParams`

**`getDraftTasks`**
- `POST` `/api/getDraftTasks`

**`getMixedPublishDetail`**
- `GET` `/api/getMixedPublishDetail`

**`getStudentTaskStatisticsByParams`**
- `GET` `/api/getStudentTaskStatisticsByParams`

**`getTaskDataCount`**
- `GET` `/api/getTaskDataCount`

**`getTaskList`**
- `GET` `/api/getTaskList`

**`getTaskPublishDisplay`**
- `GET` `/api/getTaskPublishDisplay`

**`getTaskResult`**
- `GET` `/api/getTaskResult`

**`getTaskResultList`**
- `POST` `/api/getTaskResultList`

**`getTaskStatisticsByParams`**
- `GET` `/api/getTaskStatisticsByParams`

**`getTaskTemplateDisplay`**
- `GET` `/api/getTaskTemplateDisplay`

**`getTaskUser`**
- `GET` `/api/getTaskUser`

**`homeSchool`**
- `POST` `/api/homeSchool/submit` ⚠️写

**`indicator`**
- `POST` `/evaluation/api/indicator/submitCourseEvaluation` ⚠️写

**`learningHabitsSettingPermission`**
- `GET` `/evaluation/api/learningHabitsSettingPermission`

**`learningOverviewConfigPermission`**
- `GET` `/evaluation/api/learningOverviewConfigPermission`

**`listTaskGroupByCourse`**
- `GET` `/api/listTaskGroupByCourse`

**`notes`**
- `未知` `/flashNote/api/notes/byRecordDraftId`

**`openTaskPublishResult`**
- `GET` `/api/openTaskPublishResult`

**`selectStudentByCaptureId`**
- `POST` `/api/selectStudentByCaptureId`

**`studentHomeworkCourseStatistics`**
- `GET` `/api/studentHomeworkCourseStatistics`

**`studentHomeworkCourses`**
- `GET` `/api/studentHomeworkCourses`

**`submitAchievementSendMessage`**
- `POST` `/api/submitAchievementSendMessage` ⚠️写

**`submitTaskResult`**
- `POST` `/api/submitTaskResult` ⚠️写

**`taskSubmissionRateGroupByCourse`**
- `GET` `/api/taskSubmissionRateGroupByCourse`

### 升学与招生（99）

**`enrolmentPlan`**
- `GET` `/api/enrolmentPlan`
- `GET` `/api/enrolmentPlan/acl`
- `GET` `/api/enrolmentPlan/alreadyStages`
- `POST` `/api/enrolmentPlan/alumnusList`
- `POST` `/api/enrolmentPlan/applyRecordAddOrUpdate`
- `GET` `/api/enrolmentPlan/applyRecordApplyTimeType`
- `GET` `/api/enrolmentPlan/applyRecordById`
- `POST` `/api/enrolmentPlan/applyRecordDelete`
- `未知` `/api/enrolmentPlan/applyRecordDownload`
- `GET` `/api/enrolmentPlan/applyRecordDownloadErrorInfo`
- `GET` `/api/enrolmentPlan/applyRecordDownloadErrorInfoUpdate`
- `GET` `/api/enrolmentPlan/applyRecordDownloadStudent`
- `GET` `/api/enrolmentPlan/applyRecordEnrollResultType`
- `GET` `/api/enrolmentPlan/applyRecordEnrolmentStatus`
- `GET` `/api/enrolmentPlan/applyRecordExport`
- `POST` `/api/enrolmentPlan/applyRecordIds`
- `POST` `/api/enrolmentPlan/applyRecordImport`
- `POST` `/api/enrolmentPlan/applyRecordImportNum`
- `POST` `/api/enrolmentPlan/applyRecordImportUpdate`
- `GET` `/api/enrolmentPlan/applyRecordInterviewType`
- `POST` `/api/enrolmentPlan/applyRecordList`
- `GET` `/api/enrolmentPlan/applyRecordListSortEnum`
- `GET` `/api/enrolmentPlan/applyRecordMoneyType`
- `GET` `/api/enrolmentPlan/applyRecordOfferStatusType`
- `GET` `/api/enrolmentPlan/applyRecordOfferType`
- `GET` `/api/enrolmentPlan/applyRecordSchoolYearList`
- `GET` `/api/enrolmentPlan/applyRecordStudentList`
- `POST` `/api/enrolmentPlan/applyRecordTabType`
- `GET` `/api/enrolmentPlan/baseWriteTemplateInfo`
- `GET` `/api/enrolmentPlan/batchDeleteTargetSchool` ⚠️写
- `POST` `/api/enrolmentPlan/checkFileName`
- `GET` `/api/enrolmentPlan/country`
- `GET` `/api/enrolmentPlan/deadlineType`
- `GET` `/api/enrolmentPlan/deleteSpecialtyById` ⚠️写
- `GET` `/api/enrolmentPlan/deleteTargetSchool` ⚠️写
- `GET` `/api/enrolmentPlan/enrolmentTutorStudent`
- `GET` `/api/enrolmentPlan/enrolmentTutorStudentIdList`
- `GET` `/api/enrolmentPlan/entranceExamType`
- `未知` `/api/enrolmentPlan/exportTargetSchoolByTeacher` ⚠️写
- `GET` `/api/enrolmentPlan/fileType/addOrUpdate` ⚠️写
- `POST` `/api/enrolmentPlan/fileType/batchUpload` ⚠️写
- `GET` `/api/enrolmentPlan/fileType/checkIdPermission`
- `GET` `/api/enrolmentPlan/fileType/delete` ⚠️写
- `GET` `/api/enrolmentPlan/fileType/detailById`
- `GET` `/api/enrolmentPlan/fileType/fileDelete`
- `GET` `/api/enrolmentPlan/fileType/fileEmpty`
- `GET` `/api/enrolmentPlan/fileType/fileIdList`
- `GET` `/api/enrolmentPlan/fileType/fileList`
- `未知` `/api/enrolmentPlan/fileType/getAchievementDetail`
- `GET` `/api/enrolmentPlan/fileType/infoList`
- `GET` `/api/enrolmentPlan/fileType/move` ⚠️写
- `GET` `/api/enrolmentPlan/fileType/updateFile` ⚠️写
- `POST` `/api/enrolmentPlan/fileType/upload` ⚠️写
- `GET` `/api/enrolmentPlan/fileTypeList`
- `GET` `/api/enrolmentPlan/fileTypeListNum`
- `GET` `/api/enrolmentPlan/gradeList`
- `GET` `/api/enrolmentPlan/groupList`
- `GET` `/api/enrolmentPlan/overview`
- `GET` `/api/enrolmentPlan/planCountry`
- `GET` `/api/enrolmentPlan/planCountryQuery`
- `GET` `/api/enrolmentPlan/planListByStudent`
- `GET` `/api/enrolmentPlan/possibilityType`
- `GET` `/api/enrolmentPlan/schoolYearList`
- `POST` `/api/enrolmentPlan/setEnrolmentTutor` ⚠️写
- `GET` `/api/enrolmentPlan/settingStages` ⚠️写
- `POST` `/api/enrolmentPlan/settingWriteTemplate` ⚠️写
- `POST` `/api/enrolmentPlan/specialtyAddOrUpdate`
- `GET` `/api/enrolmentPlan/specialtyByUniversity`
- `GET` `/api/enrolmentPlan/specialtyTypeByStudent`
- `GET` `/api/enrolmentPlan/specialtyTypeDelete`
- `GET` `/api/enrolmentPlan/specialtyTypeList`
- `GET` `/api/enrolmentPlan/specialtyTypeRelationInfo`
- `GET` `/api/enrolmentPlan/specialtyTypeRelationShift`
- `GET` `/api/enrolmentPlan/specialtyTypeStudentAdd`
- `POST` `/api/enrolmentPlan/specialtyTypeUpdateOrAdd`
- `GET` `/api/enrolmentPlan/studentBaseInfo`
- `GET` `/api/enrolmentPlan/studentInfo`
- `GET` `/api/enrolmentPlan/studentList`
- `GET` `/api/enrolmentPlan/targetSchoolByStudent`
- `GET` `/api/enrolmentPlan/targetSchoolByTeacher`
- `未知` `/api/enrolmentPlan/targetSchoolDownload`
- `GET` `/api/enrolmentPlan/targetSchoolDownloadErrorInfo`
- `GET` `/api/enrolmentPlan/targetSchoolDownloadErrorInfoUpdate`
- `GET` `/api/enrolmentPlan/targetSchoolDownloadStudent`
- `GET` `/api/enrolmentPlan/targetSchoolIdsByTeacher`
- `POST` `/api/enrolmentPlan/targetSchoolImport`
- `POST` `/api/enrolmentPlan/targetSchoolImportNum`
- `POST` `/api/enrolmentPlan/targetSchoolImportUpdate`
- `GET` `/api/enrolmentPlan/targetSchoolInfo`
- `POST` `/api/enrolmentPlan/targetSchoolSave`
- `GET` `/api/enrolmentPlan/universityList`
- `POST` `/api/enrolmentPlan/universityVisitRecordList`
- `POST` `/api/enrolmentPlan/visitRecordAdd`
- `GET` `/api/enrolmentPlan/visitRecordDelete`
- `GET` `/api/enrolmentPlan/visitRecordDetail`
- `POST` `/api/enrolmentPlan/visitRecordList`
- `POST` `/api/enrolmentPlan/visitRecordUpdate`
- `POST` `/api/enrolmentPlan/visitRecordUpdatePublicStatus`
- `GET` `/api/enrolmentPlan/writeTemplateInfo` ⚠️写

### 用户与权限（67）

**`user`**
- `未知` `/api/user/avatarUrl/`
- `GET` `/api/user/balance`
- `GET` `/api/user/hobby/findUserHobby`
- `POST` `/api/user/hobby/updateUserHobby` ⚠️写
- `GET` `/api/user/relation/acl`
- `GET` `/api/user/relation/checkIfCanSetStructuredListen`
- `GET` `/api/user/relation/grayFeatures`
- `GET` `/api/user/relation/listenSubjectList`
- `GET` `/api/user/relation/myRecordList`
- `GET` `/api/user/relation/stagePermission`
- `POST` `/api/user/relation/updateIsPublic` ⚠️写

**`studentManagement`**
- `GET` `/calendar/api/studentManagement`
- `GET` `/calendar/api/studentManagement/grade`
- `POST` `/calendar/api/studentManagement/listStudentDetail`
- `GET` `/calendar/api/studentManagement/parent/grade`
- `GET` `/calendar/api/studentManagement/studentInfo`
- `POST` `/calendar/api/studentManagement/studentSearch`

**`acl`**
- `GET` `/api/acl/adminClassList`
- `GET` `/api/acl/gradeList`
- `GET` `/api/acl/stageList`
- `GET` `/api/acl/subjectList`

**`student`**
- `GET` `/api/student/detail`
- `GET` `/course/api/student/roster/listStu`
- `未知` `/iot/api/student/intimacy`
- `未知` `/iot/api/student/macAddress`

**`school`**
- `GET` `/api/school/theme/detail`
- `GET` `/api/school/theme/permission`
- `POST` `/api/school/theme/save` ⚠️写

**`all`**
- `GET` `/api/all/grade`
- `GET` `/evaluation/api/all/grade`

**`choose`**
- `POST` `/course/api/choose/batchStudent/roster/list` ⚠️写
- `GET` `/course/api/choose/batchStudent/roster/list/export` ⚠️写

**`current`**
- `GET` `/api/current/user/identity`
- `POST` `/task/api/current/user/identity`

**`currentUser`**
- `GET` `/api/currentUser`
- `GET` `/evaluation/api/currentUser`

**`photo`**
- `GET` `/api/photo/getMyClassOrGrade`
- `GET` `/api/photo/getStudentsInfoByIdClient`

**`profile`**
- `GET` `/api/profile/advanced`
- `GET` `/api/profile/basic`

**`public`**
- `未知` `/agent-max/api/public/assistants/by-school/`
- `未知` `/api/public/assistants/by-school/`

**`check`**
- `GET` `/api/check/permission`

**`checkPermission`**
- `GET` `/api/checkPermission`

**`checkPermissions`**
- `GET` `/api/checkPermissions`

**`currentIdentity`**
- `GET` `/api/currentIdentity`

**`export_student`**
- `GET` `/api/export_student` ⚠️写

**`getAllSchool`**
- `GET` `/api/getAllSchool`

**`getAllStudents`**
- `GET` `/api/getAllStudents`

**`getLearningFilePermission`**
- `GET` `/api/getLearningFilePermission`

**`getStudentsByRole`**
- `GET` `/api/getStudentsByRole`

**`list`**
- `GET` `/api/list/all/subject`

**`listGrade`**
- `GET` `/api/listGrade`

**`listSchoolConfig`**
- `POST` `/api/listSchoolConfig`

**`login`**
- `POST` `/api/login/account`

**`myStageAndSubject`**
- `GET` `/api/myStageAndSubject`

**`new`**
- `POST` `/api/new/student/list`

**`newGetStageAndSubject`**
- `GET` `/api/newGetStageAndSubject`

**`permission`**
- `GET` `/api/permission/isPermission`

**`register`**
- `POST` `/api/register`

**`result`**
- `GET` `/evaluation/api/result/getStudentGraphResultList`

**`role`**
- `GET` `/course/api/role/baseTag/roleList`

**`roleName`**
- `GET` `/calendar/api/roleName`

**`saveSchoolConfig`**
- `POST` `/api/saveSchoolConfig` ⚠️写

**`studentInfoAndSubmissionRate`**
- `GET` `/api/studentInfoAndSubmissionRate`

**`toLogout`**
- `未知` `/api/toLogout`

**`users`**
- `GET` `/api/users`

### 统计与看板（53）

**`statistics`**
- `未知` `/api/statistics/college/analyze/rank/export` ⚠️写
- `未知` `/api/statistics/creator/analyze/rank/export` ⚠️写
- `未知` `/api/statistics/grade/analyze/rank/export` ⚠️写
- `未知` `/api/statistics/grade/student/analyze/rank/export` ⚠️写
- `GET` `/api/statistics/permission`
- `未知` `/api/statistics/student/analyze/rank/export` ⚠️写
- `GET` `/calendar/api/statistics`
- `POST` `/calendar/api/statistics/class/analyze/overview`
- `POST` `/calendar/api/statistics/class/creator/analyze/rank`
- `POST` `/calendar/api/statistics/class/grade/analyze/rank`
- `POST` `/calendar/api/statistics/college/analyze/overview`
- `POST` `/calendar/api/statistics/college/analyze/rank`
- `POST` `/calendar/api/statistics/creator/analyze/rank`
- `POST` `/calendar/api/statistics/diagnosis/stu`
- `POST` `/calendar/api/statistics/distributionChartDetails`
- `POST` `/calendar/api/statistics/distributionChartDetails/V2`
- `POST` `/calendar/api/statistics/distributionChartDetails/V3`
- `POST` `/calendar/api/statistics/distributionChartDetails/radar`
- `POST` `/calendar/api/statistics/grade/analyze/overview`
- `POST` `/calendar/api/statistics/grade/analyze/rank`
- `POST` `/calendar/api/statistics/grade/student/analyze/rank`
- `GET` `/calendar/api/statistics/listCampus`
- `GET` `/calendar/api/statistics/rule/listRankRule`
- `POST` `/calendar/api/statistics/rule/updateRankRule` ⚠️写
- `POST` `/calendar/api/statistics/saveOrUpdate/diagnosis` ⚠️写
- `POST` `/calendar/api/statistics/stu/analyze`
- `未知` `/calendar/api/statistics/stu/analyze/export` ⚠️写
- `GET` `/calendar/api/statistics/stu/dayAnalyze`
- `GET` `/calendar/api/statistics/stu/detail`
- `POST` `/calendar/api/statistics/student/analyze/rank`
- `POST` `/calendar/api/statistics/studentDetail`

**`analytics`**
- `未知` `/api/analytics`
- `GET` `/api/analytics/report`
- `GET` `/api/analytics/report/cioAuthority`
- `GET` `/api/analytics/reportByClientType`
- `GET` `/api/analytics/reportByClientTypeWithUserDetail`
- `GET` `/api/analytics/reportBySchool`

**`board`**
- `GET` `/api/board`
- `GET` `/api/board/getTobeDoneUserInfo`
- `GET` `/api/board/gradeList`
- `GET` `/api/board/gradeListByTree`

**`getLearningOverviewConfig`**
- `GET` `/api/getLearningOverviewConfig`
- `GET` `/evaluation/api/getLearningOverviewConfig`

**`user`**
- `GET` `/api/user/relation/listenStatistics`
- `GET` `/api/user/relation/listenStatisticsV3`

**`fake_chart_data`**
- `GET` `/api/fake_chart_data`

**`ifEditStuBoardPermission`**
- `GET` `/api/ifEditStuBoardPermission`

**`ifShowLearningOverview`**
- `GET` `/evaluation/api/ifShowLearningOverview`

**`listLearningOverview`**
- `GET` `/api/listLearningOverview`

**`listLearningOverviewConfig`**
- `GET` `/api/listLearningOverviewConfig`

**`listModuleContentOfStuBoard`**
- `GET` `/api/listModuleContentOfStuBoard`

**`saveLearningOverviewConfig`**
- `POST` `/evaluation/api/saveLearningOverviewConfig` ⚠️写

**`saveModuleContentOfStuBoard`**
- `POST` `/api/saveModuleContentOfStuBoard` ⚠️写

### 课表与日程（50）

**`plan`**
- `未知` `/api/plan/`
- `POST` `/api/plan/addOrUpdate` ⚠️写
- `POST` `/api/plan/addOrUpdateWeek` ⚠️写
- `GET` `/api/plan/delete` ⚠️写
- `POST` `/api/plan/deleteDay` ⚠️写
- `POST` `/api/plan/deleteWeek` ⚠️写
- `POST` `/api/plan/detail`
- `POST` `/api/plan/detailWeek`
- `GET` `/api/plan/detailWeekOfParent`
- `GET` `/api/plan/getPlanWeekListByOrgIdAndPlanId`
- `GET` `/api/plan/listWeekOfParent`
- `POST` `/api/plan/pageList`
- `POST` `/api/plan/pageListPlanDay`
- `POST` `/api/plan/pageListPlanWeek`
- `GET` `/api/plan/sendDayPlanMessage` ⚠️写
- `GET` `/api/plan/sendWeekPlanMessage` ⚠️写
- `GET` `/api/plan/subjectByStage`
- `POST` `/api/plan/updateStatus` ⚠️写
- `POST` `/api/plan/updateStatusByPlanDayId` ⚠️写
- `POST` `/api/plan/updateStatusByPlanWeekId` ⚠️写

**`homeSchool`**
- `GET` `/api/homeSchool/chiefTutorInfoByStudentAndSemester`
- `GET` `/api/homeSchool/currentSemesterId`
- `GET` `/api/homeSchool/groupInfoByStudentAndSemester`
- `GET` `/api/homeSchool/semesterList`
- `GET` `/api/homeSchool/tutorInfoByStudentAndSemester`

**`all`**
- `GET` `/api/all/semester`
- `GET` `/evaluation/api/all/gradeSemesterList`
- `GET` `/evaluation/api/all/semester`

**`board`**
- `GET` `/api/board/getMonthBySemester`
- `GET` `/api/board/getYearAndSemesterList`

**`growthRecord`**
- `GET` `/api/growthRecord/bySemester`
- `GET` `/api/growthRecord/semesterList`

**`schoolYear`**
- `GET` `/api/schoolYear`
- `GET` `/course/api/schoolYear/listSchoolYear`

**`statistics`**
- `GET` `/calendar/api/statistics/currentSemester`
- `GET` `/calendar/api/statistics/getTime`

**`timeMachine`**
- `GET` `/api/timeMachine/getDataByPlanIdAndStudentUserId`
- `GET` `/api/timeMachine/listTimeMachinePlanModuleOfStuBoard`

**`currentSemester`**
- `GET` `/api/currentSemester/rangeTime`

**`currentStageList`**
- `GET` `/api/currentStageList`

**`currentTimeToSemester`**
- `GET` `/api/currentTimeToSemester`

**`exchange`**
- `POST` `/calendar/api/exchange/count/semester` ⚠️写

**`get`**
- `GET` `/api/get/semester`

**`getSemesterByYearId`**
- `GET` `/api/getSemesterByYearId`

**`listYearAndSemester`**
- `GET` `/api/listYearAndSemester`

**`punctualitySubmissionRateOfSemester`**
- `GET` `/api/punctualitySubmissionRateOfSemester`

**`recipe`**
- `GET` `/iot/api/recipe/allSemester`

**`sport`**
- `GET` `/iot/api/sport/getTimeSportBymac`

**`stage`**
- `GET` `/api/stage/list`

**`user`**
- `GET` `/api/user/relation/semesterStatistics`

### 考勤与请假（35）

**`school`**
- `GET` `/course/api/school/getAttendance`
- `GET` `/course/api/school/getEnteringLeavingSetting`
- `GET` `/course/api/school/getLateTime`
- `GET` `/course/api/school/getStageAttendance`
- `GET` `/course/api/school/listLeaveConfig`
- `POST` `/course/api/school/setEnteringLeavingSetting` ⚠️写
- `POST` `/course/api/school/updateAttendance` ⚠️写
- `POST` `/course/api/school/updateLateTime` ⚠️写
- `未知` `/course/api/school/updateStageAttendance` ⚠️写

**`leaveConfig`**
- `GET` `/api/leaveConfig/list`
- `POST` `/api/leaveConfig/update` ⚠️写
- `GET` `/leave/api/leaveConfig/checkPermission`
- `GET` `/leave/api/leaveConfig/list`
- `GET` `/leave/api/leaveConfig/listStage`
- `GET` `/leave/api/leaveConfig/schoolLeaveConfig`
- `POST` `/leave/api/leaveConfig/update` ⚠️写

**`statistics`**
- `GET` `/calendar/api/statistics/exportStudentClassAttendanceStatistics` ⚠️写
- `POST` `/calendar/api/statistics/leaveStatistics`
- `GET` `/calendar/api/statistics/leaveStatisticsSwitch`
- `POST` `/calendar/api/statistics/listAttendanceStatistics`
- `POST` `/calendar/api/statistics/listLeave`

**`leaveFlow`**
- `GET` `/leave/api/leaveFlow/config/detail`
- `GET` `/leave/api/leaveFlow/config/enabled` ⚠️写
- `POST` `/leave/api/leaveFlow/config/simulate`

**`leave`**
- `POST` `/api/leave/reasonReviewApprove`
- `GET` `/leave/api/leave/reasonReview/permission`

**`batchUpdateStudentAttendanceDetail`**
- `POST` `/calendar/api/batchUpdateStudentAttendanceDetail` ⚠️写

**`checkAttendanceSetting`**
- `GET` `/calendar/api/checkAttendanceSetting`

**`listAttendanceStatus`**
- `GET` `/calendar/api/listAttendanceStatus`

**`listDormAttendance`**
- `POST` `/calendar/api/listDormAttendance`

**`listStudentAttendanceDetail`**
- `POST` `/calendar/api/listStudentAttendanceDetail`

**`listStudentsAttendance`**
- `POST` `/calendar/api/listStudentsAttendance`

**`query`**
- `POST` `/calendar/api/query/listAttendanceStudent`

**`showAttendanceSetting`**
- `GET` `/calendar/api/showAttendanceSetting`

**`updateStudentAttendanceDetail`**
- `POST` `/calendar/api/updateStudentAttendanceDetail` ⚠️写

### 其他（28）

**`habit`**
- `未知` `/evaluation/api/habit`
- `GET` `/evaluation/api/habit/deletedHabitGradeExtends` ⚠️写
- `GET` `/evaluation/api/habit/listHabitTree`
- `POST` `/evaluation/api/habit/saveHabitGradeExtends` ⚠️写
- `POST` `/evaluation/api/habit/updateHabitGradeExtends` ⚠️写

**`activities`**
- `GET` `/api/activities`

**`checkCCA`**
- `GET` `/calendar/api/checkCCA`

**`current`**
- `GET` `/iot/api/current/userNew`

**`deleteCommonPhrasesById`**
- `GET` `/calendar/api/deleteCommonPhrasesById` ⚠️写

**`deleteCommonPhrasesClassificationById`**
- `GET` `/calendar/api/deleteCommonPhrasesClassificationById` ⚠️写

**`exchange`**
- `POST` `/calendar/api/exchange/count` ⚠️写

**`general`**
- `未知` `/center/api/general/translate`

**`getCommonPhrases`**
- `GET` `/calendar/api/getCommonPhrases`

**`getCommonPhrasesClassification`**
- `GET` `/calendar/api/getCommonPhrasesClassification`

**`listLearningHabitsAlias`**
- `GET` `/evaluation/api/listLearningHabitsAlias`

**`public`**
- `未知` `/agent-max/api/public/pagelab/tools`

**`query`**
- `GET` `/calendar/api/query/statusStatistic`

**`rank`**
- `GET` `/calendar/api/rank`

**`saveCommonPhrases`**
- `POST` `/calendar/api/saveCommonPhrases` ⚠️写

**`saveCommonPhrasesClassification`**
- `POST` `/calendar/api/saveCommonPhrasesClassification` ⚠️写

**`saveLearningHabitsAlias`**
- `POST` `/evaluation/api/saveLearningHabitsAlias` ⚠️写

**`search`**
- `GET` `/calendar/api/search/grades`

**`stuDayAnalyze`**
- `POST` `/calendar/api/stuDayAnalyze`

**`transcloudIntegralList`**
- `GET` `/api/transcloudIntegralList`

**`updateAll`**
- `GET` `/calendar/api/updateAll` ⚠️写

**`updateDescription`**
- `GET` `/api/updateDescription` ⚠️写

**`updatePersonDefault`**
- `GET` `/api/updatePersonDefault` ⚠️写

**`updateStatus`**
- `POST` `/calendar/api/updateStatus` ⚠️写

### 成长目标与档案（27）

**`growthRecord`**
- `GET` `/api/growthRecord`
- `未知` `/api/growthRecord/board/gradeList`
- `未知` `/api/growthRecord/board/groupList`
- `GET` `/api/growthRecord/honorTypeList`
- `GET` `/api/growthRecord/kindergartenTemplate`

**`target`**
- `GET` `/api/target/check/delete` ⚠️写
- `POST` `/api/target/create` ⚠️写
- `POST` `/api/target/delete` ⚠️写
- `GET` `/api/target/sort`
- `POST` `/api/target/update` ⚠️写

**`board`**
- `GET` `/api/board/recordInfoList`
- `未知` `/api/board/recordInfoListReport`

**`user`**
- `GET` `/api/user/relation/recordList`
- `未知` `/api/user/relation/recordListExport`

**`addImpression`**
- `POST` `/api/addImpression` ⚠️写

**`agreedImpression`**
- `POST` `/api/agreedImpression`

**`deleteImpression`**
- `GET` `/api/deleteImpression` ⚠️写

**`deletedActivity`**
- `GET` `/api/deletedActivity` ⚠️写

**`getActivity`**
- `GET` `/api/getActivity`

**`growthAim`**
- `GET` `/evaluation/api/growthAim/aimFootprintStudent`

**`homeSchool`**
- `GET` `/api/homeSchool/studentGrowthAim`

**`insertActivity`**
- `POST` `/api/insertActivity` ⚠️写

**`isDeletedActivity`**
- `GET` `/api/isDeletedActivity`

**`poster`**
- `GET` `/api/poster/info`

**`updateActivity`**
- `POST` `/api/updateActivity` ⚠️写

**`updateActivitySort`**
- `GET` `/api/updateActivitySort` ⚠️写

**`updateTarget`**
- `POST` `/api/updateTarget` ⚠️写

### 文件与媒体（21）

**`photo`**
- `POST` `/api/photo/batchUploadTemplate` ⚠️写
- `GET` `/api/photo/downloadFile`
- `未知` `/api/photo/preview_file`

**`fileContent`**
- `GET` `/api/fileContent/list`
- `GET` `/api/fileContent/selectByFileId`

**`upload_file`**
- `GET` `/api/upload_file` ⚠️写
- `GET` `/api/upload_file/new` ⚠️写

**`batch`**
- `POST` `/api/batch/upload_file/new` ⚠️写

**`demoExport`**
- `GET` `/api/demoExport`

**`file`**
- `未知` `/api/file/preview`

**`file-services`**
- `GET` `/center/api/file-services/getFileAnalysisResult`

**`getFileBatch`**
- `未知` `/api/getFileBatch`

**`imageRotate`**
- `GET` `/api/imageRotate/updateImageRotate` ⚠️写

**`new_download_file`**
- `未知` `/api/new_download_file`

**`preview_file`**
- `未知` `/api/preview_file`

**`record`**
- `GET` `/api/record/screen/file/list`

**`sts`**
- `GET` `/api/sts/token`

**`stuDayExportCode`**
- `GET` `/calendar/api/stuDayExportCode`

**`update_fileName`**
- `POST` `/api/update_fileName` ⚠️写

**`upload`**
- `POST` `/api/upload/shareFile` ⚠️写

**`upload_link`**
- `GET` `/api/upload_link` ⚠️写

### 阅读（19）

**`read`**
- `GET` `/api/read/detailById`
- `GET` `/api/read/dynamicList`
- `GET` `/api/read/listStatistics`
- `GET` `/api/read/statistics`
- `GET` `/api/read/yesterdayStatistics`

**`export`**
- `未知` `/api/export/readData/statistics` ⚠️写
- `未知` `/api/export/readRecord` ⚠️写

**`readRecord`**
- `GET` `/api/readRecord`
- `GET` `/api/readRecord/student`

**`addReadComment`**
- `POST` `/api/addReadComment` ⚠️写

**`deletedReadComment`**
- `GET` `/api/deletedReadComment` ⚠️写

**`getMyReadBooks`**
- `GET` `/api/getMyReadBooks/byMonth`

**`getMyReadInfo`**
- `GET` `/api/getMyReadInfo/byRange`

**`getMyReadStatistics`**
- `GET` `/api/getMyReadStatistics`

**`messageCenter`**
- `POST` `/api/messageCenter/read`

**`readBooks`**
- `GET` `/api/readBooks/byRange`

**`readData`**
- `GET` `/api/readData/statistics`

**`readDate`**
- `GET` `/api/readDate`

**`readSort`**
- `GET` `/api/readSort/statistics`

### AI 功能（12）

**`prefixPrompt`**
- `GET` `/api/prefixPrompt/list`
- `POST` `/api/prefixPrompt/update` ⚠️写

**`ai`**
- `GET` `/api/ai/grade/list`

**`batchCreateAIResultByPlanId`**
- `GET` `/evaluation/api/batchCreateAIResultByPlanId` ⚠️写

**`createOrEditAITopic`**
- `POST` `/api/createOrEditAITopic` ⚠️写

**`getAIApps`**
- `未知` `/api/getAIApps`

**`getAIConversionForTopic`**
- `GET` `/api/getAIConversionForTopic`

**`getAITopicsList`**
- `GET` `/api/getAITopicsList`

**`getDetail`**
- `GET` `/api/getDetail`

**`getPrefixPromptPersonFlag`**
- `GET` `/api/getPrefixPromptPersonFlag`

**`saveAIConversionForTopic`**
- `POST` `/api/saveAIConversionForTopic` ⚠️写

**`stu`**
- `POST` `/calendar/api/stu/detail/analyzeJSONExplain`

### 配置与字典（12）

**`1`**
- `GET` `/api/1/item/`

**`appValueConfig`**
- `GET` `/api/appValueConfig`

**`config`**
- `GET` `/api/config/get`

**`dict`**
- `GET` `/api/dict/hobby`

**`fake_list`**
- `GET` `/api/fake_list`

**`forms`**
- `POST` `/api/forms`

**`mock`**
- `GET` `/api/mock/changeAccount`

**`model`**
- `GET` `/api/model/list`

**`queryEdit`**
- `GET` `/api/queryEdit`

**`rule`**
- `GET` `/api/rule`

**`set_language`**
- `POST` `/api/set_language` ⚠️写

**`tags`**
- `GET` `/api/tags`

### 消息与通知（9）

**`messageCenter`**
- `GET` `/api/messageCenter/count`
- `GET` `/api/messageCenter/page`

**`alarm`**
- `未知` `/api/alarm` ⚠️写

**`conversation`**
- `POST` `/api/conversation`

**`hurry`**
- `GET` `/api/hurry` ⚠️写

**`listChatGPTUsageAmountBySchoolId`**
- `GET` `/api/listChatGPTUsageAmountBySchoolId`

**`notices`**
- `GET` `/api/notices`

**`project`**
- `GET` `/api/project/notice`

**`school`**
- `GET` `/course/api/school/getMessageRemainingCount`

### 互动与点赞（6）

**`addLike`**
- `GET` `/api/addLike` ⚠️写

**`cancelZan`**
- `POST` `/api/cancelZan`

**`deletedCommentary`**
- `GET` `/api/deletedCommentary` ⚠️写

**`deletedLike`**
- `GET` `/api/deletedLike` ⚠️写

**`saveCommentary`**
- `POST` `/api/saveCommentary` ⚠️写

**`saveZan`**
- `POST` `/api/saveZan` ⚠️写

### 健康与体育（2）

**`health`**
- `GET` `/health/api/health/periodic-review/aiDetail`
- `POST` `/health/api/health/periodic-review/updateHealthAIAdvice` ⚠️写
