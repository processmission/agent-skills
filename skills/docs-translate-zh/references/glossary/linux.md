<!-- SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission -->
<!-- SPDX-License-Identifier: MIT -->

# Linux 术语附录

整理日期：2026-09-28。共 47 项。英文来源用于核对语境，**不表示中文译名获得官方认可**。
中文为本 skill 的项目建议译法，尚未人工审定；没有中文的条目暂保留英文。
采用中文时，每次写作 `中文（本行英文原名）`。变量、命令、类型与引用目标不改写。
查阅 [使用说明与扫描工具](../term-scan.md)；多义词须先核对上下文。

| English | 中文 | 策略 | 语境与注意事项 | 来源 |
| --- | --- | --- | --- | --- |
| anonymous memory | 匿名内存 | bilingual | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| call_rcu |  | keep-English | RCU 同步与对象生命周期 | [原文](https://docs.kernel.org/RCU/whatisRCU.html) |
| critical section | 临界区 | bilingual | 锁与抢占；类型名原样保留 | [原文](https://docs.kernel.org/locking/locktypes.html) |
| grace period | 宽限期 | bilingual | RCU 同步与对象生命周期 | [原文](https://docs.kernel.org/RCU/whatisRCU.html) |
| huge page | 大页 | bilingual | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| hugetlbfs |  | keep-English | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| kcompactd |  | keep-English | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| kernel | 内核 | bilingual | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| kswapd |  | keep-English | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| Linux |  | keep-English | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| local_lock |  | keep-English | 锁与抢占；类型名原样保留 | [原文](https://docs.kernel.org/locking/locktypes.html) |
| memory compaction | 内存规整 | bilingual | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| MMU |  | keep-English | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| mutex | 互斥锁 | bilingual | 锁与抢占；类型名原样保留 | [原文](https://docs.kernel.org/locking/locktypes.html) |
| NUMA |  | keep-English | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| OOM killer |  | keep-English | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| page cache | 页缓存 | bilingual | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| page frame | 页框 | bilingual | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| page table | 页表 | bilingual | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| physical address | 物理地址 | bilingual | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| physical memory | 物理内存 | bilingual | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| PREEMPT_RT |  | keep-English | 锁与抢占；类型名原样保留 | [原文](https://docs.kernel.org/locking/locktypes.html) |
| preemption | 抢占 | bilingual | 锁与抢占；类型名原样保留 | [原文](https://docs.kernel.org/locking/locktypes.html) |
| priority inheritance | 优先级继承 | bilingual | 锁与抢占；类型名原样保留 | [原文](https://docs.kernel.org/locking/locktypes.html) |
| priority inversion | 优先级反转 | bilingual | 锁与抢占；类型名原样保留 | [原文](https://docs.kernel.org/locking/locktypes.html) |
| quiescent state | 静止状态 | bilingual | RCU 同步与对象生命周期 | [原文](https://docs.kernel.org/RCU/whatisRCU.html) |
| raw_spinlock_t |  | keep-English | 锁与抢占；类型名原样保留 | [原文](https://docs.kernel.org/locking/locktypes.html) |
| RCU |  | keep-English | RCU 同步与对象生命周期 | [原文](https://docs.kernel.org/RCU/whatisRCU.html) |
| rcu_read_lock |  | keep-English | RCU 同步与对象生命周期 | [原文](https://docs.kernel.org/RCU/whatisRCU.html) |
| rcu_read_unlock |  | keep-English | RCU 同步与对象生命周期 | [原文](https://docs.kernel.org/RCU/whatisRCU.html) |
| read-side critical section | 读侧临界区 | bilingual | RCU 同步与对象生命周期 | [原文](https://docs.kernel.org/RCU/whatisRCU.html) |
| reclaim | 回收 | bilingual | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| rt_mutex |  | keep-English | 锁与抢占；类型名原样保留 | [原文](https://docs.kernel.org/locking/locktypes.html) |
| rw_semaphore |  | keep-English | 锁与抢占；类型名原样保留 | [原文](https://docs.kernel.org/locking/locktypes.html) |
| rwlock_t |  | keep-English | 锁与抢占；类型名原样保留 | [原文](https://docs.kernel.org/locking/locktypes.html) |
| semaphore | 信号量 | bilingual | 锁与抢占；类型名原样保留 | [原文](https://docs.kernel.org/locking/locktypes.html) |
| spinlock | 自旋锁 | bilingual | 锁与抢占；类型名原样保留 | [原文](https://docs.kernel.org/locking/locktypes.html) |
| spinlock_t |  | keep-English | 锁与抢占；类型名原样保留 | [原文](https://docs.kernel.org/locking/locktypes.html) |
| SRCU |  | keep-English | RCU 同步与对象生命周期 | [原文](https://docs.kernel.org/RCU/whatisRCU.html) |
| synchronize_rcu |  | keep-English | RCU 同步与对象生命周期 | [原文](https://docs.kernel.org/RCU/whatisRCU.html) |
| THP |  | keep-English | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| TLB |  | keep-English | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| virtual address | 虚拟地址 | bilingual | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| virtual memory | 虚拟内存 | bilingual | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| ZONE_DMA |  | keep-English | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| ZONE_HIGHMEM |  | keep-English | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
| ZONE_NORMAL |  | keep-English | 内存管理 | [原文](https://docs.kernel.org/admin-guide/mm/concepts.html) |
