# 研究设计Excel规则

默认文件名：`00_研究设计与证据计划_Research_Design.xlsx`

这是基础参考格式。使用者可以增加字段或工作表，但不得删除项目ID、搜索词ID、平台、时间、来源和状态等交接字段。

## 00_项目配置_Project_Config

使用纵向字段表记录：

- 项目ID / Project ID
- 项目名称 / Project Name
- 研究对象 / Research Object
- 研究市场 / Market
- 研究语言 / Languages
- 目标平台 / Platforms
- 研究开始日期 / Research Start Date
- 数据时间范围 / Data Date Range
- 研究目标 / Research Goal
- 计划交付物 / Planned Deliverables
- 明确纳入内容 / Include Rules
- 明确排除内容 / Exclude Rules
- 使用者补充要求 / User Notes
- 配置版本 / Config Version
- 最后更新时间 / Updated At

## 01_研究问题_Research_Questions

字段：

- 研究问题ID / Question ID
- 研究问题 / Research Question
- 为什么需要回答 / Decision Use
- 需要的证据 / Required Evidence
- 可用平台 / Applicable Platforms
- 对应交付物 / Deliverable
- 当前状态 / Status
- 备注 / Notes

## 02_搜索词_Search_Queries

搜索词不使用固定分类，字段用于记录形成过程：

- 搜索词ID / Query ID
- 搜索词 / Search Query
- 语言 / Language
- 平台 / Platform
- 来源 / Source
- 父搜索词ID / Parent Query ID
- 加入理由 / Reason Added
- 对应研究问题ID / Question ID
- 对应旅程阶段 / Journey Stage
- 计划用途 / Intended Use
- 状态 / Status
- 创建时间 / Created At
- 最后更新时间 / Updated At
- 备注 / Notes

`来源`建议值：使用者提供、AI初始生成、试跑扩展、已有项目。`计划用途`可以是视频内容、评论VOC或两者。

## 03_搜索试跑_Search_Pilot

字段：

- 试跑记录ID / Pilot Record ID
- 搜索词ID / Query ID
- 平台 / Platform
- 采集批次ID / Batch ID
- 试跑时间 / Pilot Time
- 请求数量 / Request Count
- 返回结果数 / Results Returned
- 相关结果数 / Relevant Results
- 重复结果数 / Duplicate Results
- 有评论视频数 / Videos With Comments
- 关键字段完整情况 / Field Availability
- 预计新增消耗 / Estimated Additional Credits
- 试跑结论 / Pilot Decision
- 调整建议 / Adjustment
- 原始数据引用 / Raw Data Reference

## 04_旅程假设_Journey_Hypothesis

此表记录研究起点，不是最终结论：

- 旅程阶段ID / Stage ID
- 主要阶段 / Primary Stage
- 次要阶段 / Secondary Stage
- 消费者主要任务 / Main Consumer Task
- 需要做出的判断 / Key Decision
- 可能需要的信息 / Expected Information Need
- 假设来源 / Hypothesis Source
- 支撑资料 / Supporting Material
- 当前版本 / Version
- 状态 / Status
- 后续需要验证什么 / Validation Needed

## 格式

- 第一行为合并的大类标题，第二行为中英文字段；
- 冻结前两行；
- 日期存为日期，数量存为数值；
- 状态字段使用下拉选项；
- 输入区使用浅黄色，系统生成字段使用浅灰色；
- 不添加装饰性仪表盘。
