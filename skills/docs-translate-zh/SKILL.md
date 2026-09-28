---
# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT
name: docs-translate-zh
description: >-
  Translate English technical documentation into faithful, natural Simplified
  Chinese with full-article context, reviewable RST or Markdown sources, and
  searchable bilingual terminology. Use for documentation translation, Chinese
  documentation maintenance, migration from fragmented PO translations, or
  verification of translated Sphinx sites and requested GitHub Pages deployment.
---

# 技术文档英译中

将英文技术文档译成适合人工审阅、能够持续维护的简体中文文档。
适用于 Zephyr、Yocto、QEMU 等项目的手写文档，也适用于其他 RST 或 Markdown 文档。

## 质量契约

- **信**：保留原文的事实、条件、否定、语气强度、适用范围及示例；不能用摘要代替翻译。
- **达**：先理解整篇文章和技术上下文，再按中文习惯组织句子；不能逐词替换。
- **雅**：表述准确、简洁、自然，保持技术文档语气；不增加宣传、评价或原文没有的解释。
- **术语可检索**：专业术语只有存在官方或适合当前语境的中文译名时才使用中文，
  每次使用均写作“中文（English）”，包括标题、目录显示文字、表格和正文。
  不得自行降为“仅首次出现标注英文”。没有可靠译名时保留英文。
- 代码、命令、标识符、路径、引用目标及其他机器解析内容保持原样；
  不向其中插入中文或括号。普通非专业词汇不必逐词附英文。
- 保留原有版权、许可证和署名。不能把另一个项目的许可声明复制到译文中。

开始翻译前读取 [术语管理](references/terminology.md) 和
[翻译与审阅](references/translation-review.md)。涉及 Sphinx、迁移、构建或发布时，
再读取 [构建与部署](references/sphinx-publishing.md)。
五个项目的具体词表及只读扫描命令见 [术语附录索引](references/term-scan.md)，
按当前项目选择附录，不需要把所有词条加载进上下文。

## 工作流程

1. **确认基线与范围**：检查仓库约定、工作区、远程和用户指定分支；统计手写文档及其
   include 文件，区分生成文档、测试夹具和外部手册。不要仅凭扩展名认定范围。
   给出简短计划；保留现有未提交修改，需要隔离时使用工作树。
2. **建立中文镜像**：使用完整文章的 RST/Markdown，保持相对路径和章节结构。
   默认中文目录为 `<文档根>/translations/zh_CN/`，其下直接镜像英文文档根，
   不再增加一层 `doc/` 或 `docs/`。已有明确布局或用户指定路径时遵循它。
   默认不用 PO，包括新建的界面翻译；修改现有 PO 体系须在任务授权范围内。
3. **建立项目术语表**：将参考文件中的模板落在项目中文维护目录，记录英文原名、
   语境、译名、证据及状态。复用已有术语决定；不确定时查一手资料或保留英文。
4. **整篇翻译**：阅读全文、相关定义和示例；保留全部技术细节，处理标题、正文、
   表格及手写说明。已有 PO 仅作为候选译文：先还原所属文章上下文，再审校写入整篇。
   源码自动生成的内容保留英文，翻译手写介绍及外围导航。
5. **分层验证**：逐段核对语义与术语；核对源文覆盖、结构、代码及引用；
   按项目方式构建并检查真实 HTML。文件齐全或构建通过均不等于语义审校完成。
6. **按授权交付**：只有用户要求时才提交、推送、配置 CI 或发布。
   交付文件、验证结果和未解决问题；发布任务还需确认对应提交的线上页面。

## 持续维护

记录上游基线提交、英文路径、英文与译文摘要值、翻译状态、审阅状态。
上游变化后先列出增删改，再结合原文差异和整篇上下文更新译文；
不能只刷新摘要值就宣称同步完成。术语变更需复查所有受影响文章。

需要多人或多 Agent 协作时，遵循当前授权与仓库规则，不默认获得分工权限。
已获授权后按完整手册或语义单元分工，明确 include 文件归属、共享术语表和文件边界；
临时文件使用各自独立目录，避免工具或草稿相互覆盖。

汇报时分别说明：源文覆盖、初译、语义审校、构建校验、线上验证。
没有人工审阅的初译不能称为“人工审定”；未发布不能称为“已上线”。
