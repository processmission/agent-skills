<!-- SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission -->
<!-- SPDX-License-Identifier: MIT -->

# QEMU 术语附录

整理日期：2026-09-28。共 67 项。英文来源用于核对语境，**不表示中文译名获得官方认可**。
中文为本 skill 的项目建议译法，尚未人工审定；没有中文的条目暂保留英文。
采用中文时，每次写作 `中文（本行英文原名）`。变量、命令、类型与引用目标不改写。
查阅 [使用说明与扫描工具](../term-scan.md)；多义词须先核对上下文。

| English | 中文 | 策略 | 语境与注意事项 | 来源 |
| --- | --- | --- | --- | --- |
| Accelerator | 加速器 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L10) |
| AddressSpace |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/loads-stores.rst#L333) |
| AioContext |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/lockcnt.rst#L167) |
| backing file | 后备文件 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/deprecated.rst#L255) |
| Block | 块 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L23) |
| block job | 块作业 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/qapi-domain.rst#L200) |
| block node | 块节点 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/interop/bitmaps.rst#L734) |
| Board | 板级模型 | bilingual | QEMU 的 machine 模型，不能照搬 Zephyr 实体开发板含义 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L18) |
| BQL |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/multi-thread-tcg.rst#L227) |
| CFI |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L31) |
| Device | 设备 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L38) |
| dirty bitmap | 脏位图 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/migration/vfio.rst#L155) |
| EDK2 |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L49) |
| gdbstub |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L56) |
| glib2 |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L63) |
| Guest | 客户机 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L79) |
| Guest agent | 客户机代理 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L71) |
| HMP |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/deprecated.rst#L70) |
| Host | 主机 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L90) |
| hotplug | 热插拔 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/reset.rst#L322) |
| HVF |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/build-platforms.rst#L46) |
| Hypervisor | 虚拟机监控器 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L96) |
| IOThread |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/multi-thread-tcg.rst#L236) |
| KVM |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/build-platforms.rst#L46) |
| live migration | 在线迁移 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/memory.rst#L135) |
| Machine | 机器模型 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L109) |
| Mailing List | 邮件列表 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L130) |
| MemoryRegion |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/memory.rst#L19) |
| Migration | 迁移 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L118) |
| MMU / softmmu |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L142) |
| Monitor / QMP / HMP |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L154) |
| MSHV |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/build-platforms.rst#L56) |
| MTTCG |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L164) |
| NBD |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L124) |
| NVMM |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/build-platforms.rst#L56) |
| Patchew |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L181) |
| Plugins | 插件 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L171) |
| PR |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L187) |
| QAPI |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/removed-features.rst#L186) |
| QCOW2 |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L197) |
| QEMU |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L205) |
| QEMU Guest Agent |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/removed-features.rst#L1504) |
| qemu-img |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/index.rst#L19) |
| qemu-nbd |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/removed-features.rst#L1379) |
| qemu-storage-daemon |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/testing/qtest.rst#L116) |
| qemu-system-aarch64 |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/emulation.rst#L528) |
| QMP |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/deprecated.rst#L68) |
| QOM |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L211) |
| qtest |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/clocks.rst#L361) |
| Record/replay | 记录与重放 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L217) |
| Rust |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L223) |
| snapshot | 快照 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/migration/CPR.rst#L146) |
| softmmu |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/build-system.rst#L86) |
| system emulation | 系统仿真 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/emulation.rst#L6) |
| System mode | 系统模式 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L230) |
| Target |  | keep-English | 多义：通常指 guest；TCG 中可指 host。逐处判定，禁止全局替换 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L242) |
| target |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/deprecated.rst#L125) |
| TCG |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L250) |
| translation block | 翻译块 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/multi-thread-tcg.rst#L55) |
| TranslationBlock |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/control-flow-integrity.rst#L105) |
| User mode | 用户模式 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L259) |
| user mode emulation | 用户模式仿真 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/emulation.rst#L6) |
| vhost-user |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L275) |
| vhost-vdpa |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/qapi-domain.rst#L139) |
| VirtIO |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/glossary.rst#L266) |
| VMStateDescription |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/devel/clocks.rst#L513) |
| WHPX |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/qemu/blob/470758c1a85a1e1d37d19b616ef5d88c8eead37d/docs/about/build-platforms.rst#L46) |
