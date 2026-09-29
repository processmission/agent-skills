<!-- SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission -->
<!-- SPDX-License-Identifier: MIT -->

# Zephyr 术语附录

整理日期：2026-09-28。共 71 项。英文来源用于核对语境，**不表示中文译名获得官方认可**。
中文为本 skill 的项目建议译法，尚未人工审定；没有中文的条目暂保留英文。
采用中文时，每次写作 `中文（本行英文原名）`。变量、命令、类型与引用目标不改写。
查阅 [使用说明与扫描工具](../term-scan.md)；多义词须先核对上下文。

| English | 中文 | 策略 | 语境与注意事项 | 来源 |
| --- | --- | --- | --- | --- |
| AMP |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/adi/max32680evkit/doc/index.rst#L211) |
| API |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L11) |
| application | 应用程序 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L15) |
| application image | 应用镜像 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L27) |
| architecture | 体系结构 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L38) |
| board | 开发板 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L41) |
| board configuration | 开发板配置 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L48) |
| board name | 开发板名称 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L56) |
| board qualifiers | 开发板限定符 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L62) |
| board revision | 开发板修订版本 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L69) |
| board target | 开发板目标 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L76) |
| CMake |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/adi/max32657evkit/doc/index.rst#L419) |
| cooperative thread | 协作式线程 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/hardware/porting/arch.rst#L295) |
| CPU cluster | CPU 簇 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L83) |
| CPU core | CPU 核心 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L90) |
| device runtime power management | 设备运行时电源管理 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L95) |
| Devicetree |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/96boards/avenger96/doc/index.rst#L178) |
| devicetree |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/96boards/avenger96/doc/index.rst#L178) |
| Devicetree binding | Devicetree 绑定 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/build/dts/api/bindings/interrupt-controller/microchip,eic-g1-intc.rst#L40) |
| DeviceTree Specification |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/build/dts/api/api.rst#L68) |
| DTB |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/amd/zynqmp_rpu/doc/index.rst#L43) |
| DTC |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/adafruit/feather_esp32s2/doc/adafruit_feather_esp32s2.rst#L156) |
| DTS |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/96boards/meerkat96/doc/index.rst#L157) |
| DTSI |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/adi/max32657evkit/doc/index.rst#L397) |
| EDK |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/qemu/x86_64/doc/index.rst#L89) |
| FCB |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/nxp/mimxrt1170_evk/doc/index.rst#L92) |
| idle thread | 空闲线程 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L102) |
| IDT |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L105) |
| internal API | 内部 API | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L110) |
| interrupt service routine | 中断服务例程 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/glossary.rst#L123) |
| ISR |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L122) |
| Kconfig |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/acrn/acrn/doc/index.rst#L43) |
| kernel | 内核 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L129) |
| LLEXT |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/releases/release-notes-3.5.rst#L12) |
| MCUboot |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/adi/max32657evkit/doc/index.rst#L348) |
| mutex | 互斥锁 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/native/nrf_bsim/doc/nrf5340bsim.rst#L39) |
| NVS |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/build/dts/api/api.rst#L558) |
| power domain | 电源域 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L133) |
| power gating | 电源门控 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L138) |
| preemptive thread | 抢占式线程 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/kernel/services/scheduling/index.rst#L156) |
| private API | 私有 API | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L142) |
| public API | 公共 API | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L149) |
| RTOS |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/404.rst#L39) |
| scheduler | 调度器 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/native/doc/arch_soc.rst#L336) |
| semaphore | 信号量 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/antmicro/stm32h7_hdmi_board/doc/index.rst#L131) |
| Settings |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/96boards/aerocore2/doc/index.rst#L198) |
| SMP |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/acrn/acrn/doc/index.rst#L60) |
| SoC |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L158) |
| SoC family | SoC 族 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L163) |
| SoC series | SoC 系列 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L167) |
| software component | 软件组件 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L171) |
| spinlock | 自旋锁 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/build/dts/api/api.rst#L298) |
| subsystem | 子系统 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L176) |
| sysbuild |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/adi/apard32690/doc/index.rst#L191) |
| system power state | 系统电源状态 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L180) |
| thread | 线程 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/adafruit/nrf52_adafruit_feather/doc/index.rst#L144) |
| Twister |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/README.rst#L15) |
| variant | 变体 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L184) |
| west |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L192) |
| west installation | west 安装环境 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L195) |
| west manifest | west 清单 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L198) |
| west manifest repository | west 清单仓库 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L204) |
| west project | west 项目 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L209) |
| west workspace | west 工作区 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L216) |
| workqueue | 工作队列 | bilingual | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/develop/tools/kapa_ai.rst#L30) |
| XIP |  | keep-English | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L223) |
| Zbus |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/releases/migration-guide-3.5.rst#L330) |
| Zephyr |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/404.rst#L8) |
| zephyr module | Zephyr 模块 | bilingual | 定义见来源；未定中文时保留英文 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/glossary.rst#L228) |
| Zephyr SDK |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/96boards/carbon/doc/nrf51822.rst#L100) |
| Ztest |  | keep-English | 项目文档用语；按来源所在子系统解释 | [原文](https://github.com/processmission/zephyr/blob/e7737db163fb0513a79069771c0f7efdf9c58150/doc/_build/local/src/boards/native/doc/bsim_boards_design.rst#L113) |
