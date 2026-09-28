<!-- SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission -->
<!-- SPDX-License-Identifier: MIT -->

# 术语附录索引与静态扫描

## 附录

当前共 319 个项目词条（跨项目同名词分别记录）：QEMU 67、Linux 47、Yocto 68、BitBake 66、Zephyr 71。

- [QEMU](glossary/qemu.md)：完整提取当前 glossary 的词条，补充仿真、迁移、块设备与对象模型术语。
- [Linux](glossary/linux.md)：内存、锁、抢占和 RCU 术语；本次本地内核源码未挂载，依据官方在线文档整理。
- [Yocto](glossary/yocto.md)：完整提取当前 terms 页的词条，补充构建工具与配置变量。
- [BitBake](glossary/bitbake.md)：依据独立官方用户手册整理元数据、语法、任务及签名相关术语。
- [Zephyr](glossary/zephyr.md)：完整提取当前 glossary 的词条，补充内核、Devicetree、构建和测试术语。

这是五个项目共用的可扩充附录，不代表已穷尽整个源码中的所有符号或技术词。
现有 glossary 的提取范围可核查；其他部分是语境明确的基础术语集。
来源支持英文术语及语境，中文译法属于项目建议，不宣称官方或人工审定。
本地来源链接固定到提取时的提交；在线 Linux 和 BitBake 来源按 2026-09-28 查阅，
后续使用须核对项目目标版本，尤其是旧变量名和新语法。

Markdown 表是唯一数据源，脚本直接读取，无需同步一份 JSON 词库。
项目需要扩展或修改时，复制所需附录到项目的术语目录，记录语境及决定，
用 `--glossary-dir` 指向该目录；不要用缺乏依据的新译名覆盖所有项目。

## 扫描工具

使用 Python 3.10 或更新版本，无第三方依赖，不访问网络、不修改输入文件。
以下命令从 skill 根目录运行；输入路径可改为任意仓库或单篇文章。

```bash
# 在英文源文定位已登记术语，输出路径、行列与所属项目。
python3 scripts/term_scan.py inventory /path/to/qemu/docs --project qemu

# 在中文文档检查已登记译名缺失或错误英文括注，以及重复括注。
python3 scripts/term_scan.py check /path/to/zh_CN --project yocto --project bitbake

# 提取尚未登记的缩写、全大写标识符和 :term: 引用，供补充词表。
python3 scripts/term_scan.py candidates /path/to/docs --project zephyr --format jsonl

# 使用项目维护的词表，并显式要求发现问题时返回非零。
python3 scripts/term_scan.py check /path/to/zh_CN --project qemu \
    --glossary-dir /path/to/project/glossary --fail-on-findings
```

不指定 `--project` 时使用全部五份表，重复指定可组合。
自定义词表目录需包含所选项目同名 Markdown 文件，沿用五列表结构；
中文列非空对应 `bilingual`，空列对应 `keep-English`，同一表英文键唯一。
含竖线的内容需要改写，当前简单表解析器不支持单元格内转义竖线。

结果默认供人工审阅，返回 0；输入或词表错误返回 2。
启用 `--fail-on-findings` 后，有结果返回 1，适用于已明确接受工具边界的流水线。
工具读取 `.rst`、`.rst.inc`、`.md`、`.txt`；去重输入，跳过目录中的符号链接文件及常见工具目录。
诊断汇总写 stderr，JSONL 结果写 stdout，便于保存报告。

## 边界与复核

这是**原始文本词法扫描**，不是 Sphinx/Markdown 语义解析器。
为避免复杂缩进把正文误吞进代码，工具不尝试通过启发式隐藏代码块；
代码、标签、URL、示例和术语表中的结果可能需要排除，不得直接自动修复。
`check` 只检查词表内已有的中文译名；无法判断漏译、错误的其他译名、未登记词或英文专名被改写。
`candidates` 也不是全量自然语言术语提取器，普通小写多词术语仍须由章节审阅补充。

检查允许括号前空白、换行、全角或半角括号和英文大小写差异；
输出建议仍采用表中的固定拼写。格式标记夹在译名与括号之间可能被报告，需看渲染结果。
同一中文对应多个英文时，所选词表内任一合法形式都会通过；
这仅说明形式匹配，语境是否正确仍须审阅。最长中文词优先，减少短词嵌套误报。

尤其核对：QEMU `target` 在普通仿真与 TCG 中含义不同；QEMU `Board` 与
Zephyr `board` 不能机械共用译名；BitBake recipe 与 package 不能混为一谈；
API 名与普通专业词、旧版与新版变量不能互相替换。
