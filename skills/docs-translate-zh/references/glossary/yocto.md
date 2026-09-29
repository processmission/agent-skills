<!-- SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission -->
<!-- SPDX-License-Identifier: MIT -->

# Yocto 术语附录

整理日期：2026-09-28。共 68 项。英文来源用于核对语境，**不表示中文译名获得官方认可**。
中文为本 skill 的项目建议译法，尚未人工审定；没有中文的条目暂保留英文。
采用中文时，每次写作 `中文（本行英文原名）`。变量、命令、类型与引用目标不改写。
查阅 [使用说明与扫描工具](../term-scan.md)；多义词须先核对上下文。

| English | 中文 | 策略 | 语境与注意事项 | 来源 |
| --- | --- | --- | --- | --- |
| Append Files | 追加文件 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L13) |
| BBLAYERS |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/brief-yoctoprojectqs/index.rst#L379) |
| BBPATH |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/bsp-manual/bsp.rst#L536) |
| BitBake |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L52) |
| bitbake-getvar |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/dev-manual/debugging.rst#L114) |
| bitbake-layers |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/brief-yoctoprojectqs/index.rst#L382) |
| Board Support Package (BSP) | 板级支持包 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L57) |
| BSP |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/brief-yoctoprojectqs/index.rst#L366) |
| Build Directory | 构建目录 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L62) |
| Build Host | 构建主机 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L111) |
| buildtools |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L116) |
| buildtools-extended |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L125) |
| buildtools-make |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L134) |
| Built-in Fragment | 内置片段 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L138) |
| Classes | 类 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L185) |
| Configuration File | 配置文件 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L192) |
| Configuration Fragment | 配置片段 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L224) |
| Container Layer | 容器层 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L266) |
| Cross-Development Toolchain | 交叉开发工具链 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L287) |
| DEPENDS |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/brief-yoctoprojectqs/index.rst#L408) |
| devtool |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/contributor-guide/recipe-style-guide.rst#L442) |
| DISTRO |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/brief-yoctoprojectqs/index.rst#L168) |
| DL_DIR |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/dev-manual/building.rst#L755) |
| eSDK |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/dev-manual/building.rst#L29) |
| Extensible Software Development Kit (eSDK) | 可扩展软件开发套件 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L309) |
| Image | 镜像 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L316) |
| IMAGE_INSTALL |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/dev-manual/build-quality.rst#L241) |
| Initramfs |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L323) |
| Layer | 层 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L365) |
| LTS |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L384) |
| MACHINE |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/brief-yoctoprojectqs/index.rst#L20) |
| Metadata | 元数据 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L390) |
| Mixin |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L409) |
| OE-Core |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/bsp-manual/bsp.rst#L224) |
| oe-init-build-env |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/bsp-manual/bsp.rst#L227) |
| OpenEmbedded |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/bitbake.rst#L9) |
| OpenEmbedded Build System | OpenEmbedded 构建系统 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L415) |
| OpenEmbedded-Core (OE-Core) |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L426) |
| Package | 软件包 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L439) |
| Package Groups | 软件包组 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L457) |
| PACKAGECONFIG |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/contributor-guide/recipe-style-guide.rst#L160) |
| Poky |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L466) |
| PREFERRED_PROVIDER |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/bsp-manual/bsp.rst#L587) |
| pseudo |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/dev-manual/external-scm.rst#L56) |
| ptest |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/contributor-guide/submit-changes.rst#L254) |
| RDEPENDS |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/contributor-guide/recipe-style-guide.rst#L166) |
| Recipe | 配方 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L506) |
| Reference Kit |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L514) |
| SBOM |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L520) |
| SDK |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/contributor-guide/submit-changes.rst#L260) |
| Source Directory | 源码目录 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L537) |
| SPDX |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L582) |
| SPDX License Expression |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L593) |
| SRC_URI |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/contributor-guide/recipe-style-guide.rst#L156) |
| SRCREV |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/bsp-manual/bsp.rst#L1425) |
| sstate |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/brief-yoctoprojectqs/index.rst#L151) |
| SSTATE_DIR |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/dev-manual/debugging.rst#L326) |
| Sysroot |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L601) |
| sysroot |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/bsp-manual/bsp.rst#L1317) |
| Task | 任务 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L626) |
| TMPDIR |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/dev-manual/building.rst#L236) |
| Toaster |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L638) |
| uninative |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/migration-guides/migration-2.1.rst#L258) |
| Upstream | 上游 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/ref-manual/terms.rst#L645) |
| Wic |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/bsp-manual/bsp.rst#L442) |
| wic |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/bsp-manual/bsp.rst#L442) |
| WORKDIR |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/dev-manual/debugging.rst#L90) |
| Yocto Project |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/yocto-docs/blob/8e4cb0ab231ad3e1ebbb88213f42258e79eb17dd/documentation/bitbake.rst#L17) |
