# 评论VOC Excel规则

默认文件名：`02_评论VOC分析_Comment_VOC.xlsx`

固定工作表：

- `00_项目配置_Project_Config`
- `01_视频来源_Video_Sources`
- `02_原始评论_Raw_Comments`
- `03_逐条理解_Comment_Analysis`
- `04_VOC主题_VOC_Themes`
- `05_旅程证据_Journey_Evidence`
- `06_内容信任_Content_Trust`

## 00_项目配置_Project_Config

保存项目ID、研究对象、市场、语言、平台、时间范围、评论范围、采集日期、当前旅程版本和配置版本。

## 01_视频来源_Video_Sources

记录评论来自哪些视频：

- 视频记录ID / Video Record ID
- 平台 / Platform
- 平台内容ID / Platform Content ID
- 视频链接 / Video URL
- 视频标题 / Video Title
- 发布者 / Publisher
- 发布时间 / Published At
- 视频内容分类 / Content Theme
- 评论范围 / Comment Scope
- 评论采集状态 / Comment Collection Status
- 原始视频数据引用 / Raw Video Reference

## 02_原始评论_Raw_Comments

### A. 来源与关联

- 评论记录ID / Comment Record ID
- 视频记录ID / Video Record ID
- 平台 / Platform
- 视频链接 / Video URL
- 采集批次ID / Collection Batch ID
- 数据采集时间 / Collected At
- 原始数据引用 / Raw Data Reference

### B. 评论身份与关系

- 平台评论ID / Platform Comment ID
- 父评论ID / Parent Comment ID
- 评论层级 / Comment Level
- 作者公开标识 / Public Author ID
- 评论发布时间 / Comment Published At

### C. 评论原文与互动

- 评论原文 / Original Comment
- 评论点赞数 / Comment Like Count
- 回复数 / Reply Count
- 回复是否完整 / Replies Complete

### D. 清洗状态

- 是否保留 / Included
- 排除原因 / Exclusion Reason
- 去重组ID / Duplicate Group ID

## 03_逐条理解_Comment_Analysis

### A. 评论关联

- 分析记录ID / Analysis ID
- 评论记录ID / Comment Record ID
- 视频记录ID / Video Record ID

### B. 语义理解

- 中文释义 / Chinese Interpretation
- 表达类型 / Expression Type
- 主要对象 / Main Object
- 用户任务或问题 / User Task or Problem
- 核心需求 / Core Need
- 需要的信息或证明 / Information or Proof Needed
- 决策或行动影响 / Decision or Action Impact
- 情绪方向 / Sentiment Direction
- 主要VOC主题 / Primary VOC Theme
- 次要VOC主题 / Secondary VOC Theme

### C. 旅程证据

- 主要旅程阶段 / Primary Journey Stage
- 次要旅程阶段 / Secondary Journey Stage
- 旅程修订信号 / Journey Revision Signal

无法对应旅程时使用`not_applicable`，不影响该评论进入内容信任分析。

### D. 内容信任信号

- 是否涉及内容信任 / Content Trust Mentioned
- 信任对象 / Trust Target
- 信任因素 / Trust Factor
- 信任方向 / Trust Direction
- 对观看或行动的影响 / Viewing or Action Effect

### E. 共鸣与复核

- 评论点赞数 / Comment Like Count
- 共鸣说明 / Resonance Note
- 是否需要人工复核 / Human Review Needed
- 人工复核原因 / Human Review Reason
- 复核结果 / Review Result

## 04_VOC主题_VOC_Themes

- 主题ID / Theme ID
- 主题名称 / Theme Name
- 主题说明 / Theme Description
- 主要用户任务 / Main User Task
- 核心需求 / Core Need
- 评论数量 / Comment Count
- 独立视频数量 / Distinct Video Count
- 点赞总量 / Total Comment Likes
- 方向分布 / Direction Mix
- 代表评论ID / Representative Comment IDs
- 反例评论ID / Counter-evidence Comment IDs
- 影响的判断或行动 / Decision or Action Impact
- 证据强弱说明 / Evidence Note

## 05_旅程证据_Journey_Evidence

- 旅程阶段ID / Stage ID
- 主要阶段 / Primary Stage
- 次要阶段 / Secondary Stage
- 消费者主要任务 / Main Consumer Task
- 关键判断 / Key Decision
- 需要的信息 / Information Need
- 评论数量 / Comment Count
- 独立视频数量 / Distinct Video Count
- 支撑评论ID / Supporting Comment IDs
- 反例评论ID / Counter-evidence Comment IDs
- 建议修订 / Proposed Revision
- 优先级依据 / Priority Rationale
- 当前旅程版本 / Journey Version

## 06_内容信任_Content_Trust

- 信任因素ID / Trust Factor ID
- 信任对象 / Trust Target
- 信任因素 / Trust Factor
- 正向评论数 / Positive Comment Count
- 负向评论数 / Negative Comment Count
- 争议评论数 / Contested Comment Count
- 独立视频数量 / Distinct Video Count
- 代表评论ID / Representative Comment IDs
- 反例评论ID / Counter-evidence Comment IDs
- 为什么影响信任 / Why It Affects Trust
- 对观看或行动的影响 / Viewing or Action Effect
- 内容启示 / Content Implication

## 格式

- 数据主表第一行为合并大类标题，第二行为双语字段；
- 冻结前两行与记录ID列；
- 评论原文不截断、不翻译覆盖；
- 评论点赞数和回复数使用数值格式；
- 缺失、失败和不适用按后台规则区分；
- 汇总表必须保留评论数量和独立视频数量；
- Excel存证据和结构化分析，完整观点与跨表结论进入Markdown报告。
