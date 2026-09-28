<!-- SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission -->
<!-- SPDX-License-Identifier: MIT -->

# BitBake 术语附录

整理日期：2026-09-28。共 66 项。英文来源用于核对语境，**不表示中文译名获得官方认可**。
中文为本 skill 的项目建议译法，尚未人工审定；没有中文的条目暂保留英文。
采用中文时，每次写作 `中文（本行英文原名）`。变量、命令、类型与引用目标不改写。
查阅 [使用说明与扫描工具](../term-scan.md)；多义词须先核对上下文。

| English | 中文 | 策略 | 语境与注意事项 | 来源 |
| --- | --- | --- | --- | --- |
| .bb |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-intro.html) |
| .bbappend |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-intro.html) |
| .bbclass |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-intro.html) |
| .conf |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-intro.html) |
| .inc |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-intro.html) |
| addhandler |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| addtask |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| anonymous Python function | 匿名 Python 函数 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| append file | 追加文件 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-intro.html) |
| BB_BASEHASH_IGNORE_VARS |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| BB_HASHBASE_WHITELIST |  | keep-English | 历史变量名；不能在旧版本示例中自动改名为 BB_BASEHASH_IGNORE_VARS | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| BB_HASHSERVE |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-execution.html) |
| BB_NUMBER_THREADS |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| BB_SIGNATURE_HANDLER |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-execution.html) |
| BB_TASKHASH |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-execution.html) |
| BBFILES |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| BBLAYERS |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| BBMULTICONFIG |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| BBPATH |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| BitBake |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-intro.html) |
| bitbake |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| bitbake-diffsigs |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| bitbake-dumpsig |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| bitbake-layers |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| BPN |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| checksum | 校验和 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-execution.html) |
| class | 类 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-intro.html) |
| configuration file | 配置文件 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-intro.html) |
| deltask |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| DEPENDS |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| do_compile |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| do_configure |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| do_fetch |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| do_install |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| do_patch |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| do_populate_sysroot |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| do_unpack |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| EXPORT_FUNCTIONS |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| fetcher | 获取器 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-fetching.html) |
| FILESPATH |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-fetching.html) |
| hash equivalence |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-execution.html) |
| immediate variable expansion | 立即变量展开 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| include |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| inherit |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| inherit_defer |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| inheritance | 继承 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| layer | 层 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-intro.html) |
| metadata | 元数据 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-intro.html) |
| multiconfig |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| override | 覆盖 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| OVERRIDES |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| PN |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| PR |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| PROVIDES |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| PV |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| RDEPENDS |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| recipe | 配方 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-intro.html) |
| require |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| runqueue |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-execution.html) |
| setscene |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-execution.html) |
| signature | 签名 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-execution.html) |
| SRC_URI |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-fetching.html) |
| SRCREV |  | keep-English | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-fetching.html) |
| task | 任务 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-intro.html) |
| variable expansion | 变量展开 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
| variable flag | 变量标志 | bilingual | 构建元数据语境；语法、变量和任务标识符保留原样 | [原文](https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html) |
