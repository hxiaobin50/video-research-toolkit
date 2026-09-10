# 视频内容调研Excel规则

默认文件名：`01_视频内容调研_Video_Landscape.xlsx`

固定工作表：

- `00_项目配置_Project_Config`
- `01_搜索词_Search_Queries`
- `02_视频主表_Video_Master`
- `03_人工观看_Manual_Review`

Excel是基础参考格式。允许增加业务字段，但必须保留系统标识、来源、时间、原始数据引用和关键关联字段。

## 00_项目配置_Project_Config

保存当前项目配置快照，包括项目ID、研究对象、市场、语言、平台、时间范围、研究目标、纳入排除规则、采集日期、配置版本和备注。

## 01_搜索词_Search_Queries

保存本次内容调研实际使用的搜索词，不强制固定分类：

- 搜索词ID / Query ID
- 搜索词 / Search Query
- 语言 / Language
- 平台 / Platform
- 来源 / Source
- 父搜索词ID / Parent Query ID
- 加入理由 / Reason Added
- 状态 / Status
- 返回结果数 / Results Returned
- 相关结果数 / Relevant Results
- 新增唯一视频数 / New Unique Videos
- 执行时间 / Executed At
- 备注 / Notes

## 02_视频主表_Video_Master

第一行必须包含合并的大类标题，第二行包含双语字段标题。

### A. 视频身份与采集来源

- 记录ID / Record ID
- 平台 / Platform
- 平台内容ID / Platform Content ID
- 视频链接 / Video URL
- 平台内容类型 / Platform Content Type
- 同内容组ID / Same Content Group ID
- 发现方式 / Discovery Method
- 来源搜索词ID / Source Query ID
- 采集批次ID / Collection Batch ID
- 数据采集时间 / Collected At
- 原始数据引用 / Raw Data Reference

### B. 视频内容基础信息

- 视频标题 / Video Title
- 发布者名称 / Publisher Name
- 发布者ID / Publisher ID
- 发布时间 / Published At
- 时长秒数 / Duration Seconds
- 时长区间 / Duration Band
- 视频描述 / Description
- 可用文字摘要 / Available Text Summary

时长区间固定为：`0–30秒`、`31–60秒`、`61–120秒`、`>120秒`，边界不重叠。不要求保存完整字幕。

### C. 平台表现数据

- 播放或观看数 / View or Play Count
- 点赞数 / Like Count
- 评论数 / Comment Count
- 分享数 / Share Count
- 收藏数 / Save Count
- 点赞率 / Like Rate
- 评论率 / Comment Rate
- 分享率 / Share Rate
- 收藏率 / Save Rate

不同平台无法提供的指标使用`not_available`。比例由系统计算，不要求使用者填写。

### D. 研究分类

- 相关性 / Relevance
- 排除原因 / Exclusion Reason
- 主要旅程阶段 / Primary Journey Stage
- 消费者主要任务 / Main Consumer Task
- 次要旅程阶段 / Secondary Journey Stage
- 主要内容主题 / Primary Content Theme
- 次要内容主题 / Secondary Content Theme
- 目标用户类型 / Target Audience Type

目标用户只有存在明确证据时填写。分类依据不另设长文本字段，必要证据保留在人工观看表或处理记录中。

### E. 人工观看

- 是否需要人工观看 / Manual Review Needed
- 人工观看原因 / Manual Review Reason

不需要人工观看时，原因统一填写“无需观看”。

## 03_人工观看_Manual_Review

### A. 视频关联

- 观看记录ID / Review ID
- 视频记录ID / Video Record ID
- 平台 / Platform
- 视频链接 / Video URL
- 视频标题 / Video Title

### B. 入选与观看

- 入选类型 / Selection Type
- 入选原因 / Selection Reason
- 观看日期 / Reviewed At
- 观看完整度 / Review Coverage

入选类型建议值：优秀长视频、优秀短视频、AI无法可靠判断、使用者指定。

### C. 实际观察

- 实际主要任务 / Observed Main Task
- 实际主要内容 / Observed Main Content
- 开头吸引方式 / Opening Hook
- 内容结构与节奏 / Structure and Pacing
- 关键演示或证据 / Demonstration or Proof
- 演讲者与表达 / Speaker and Delivery
- 拍摄剪辑特点 / Filming and Editing
- 关键时间点 / Key Timestamps
- 行动引导 / Call to Action

### D. 研究价值

- 评论反馈对应情况 / Comment Alignment
- 可复制机制 / Replicable Mechanism
- 不可复制条件 / Non-replicable Conditions
- 对报告的启示 / Report Implication
- 复核备注 / Review Notes

## 格式

- 所有主表第一行为合并大类标题，第二行为双语字段；
- 冻结前两行与必要的左侧标识列；
- 长文本自动换行并顶端对齐；
- 数量使用数值格式，比例使用百分比格式，日期使用可排序日期；
- 不用0代替缺失数据；
- 不预置固定内容分类下拉框，避免限制品类；
- 可以为状态类字段设置下拉选项。
