<!-- SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission -->
<!-- SPDX-License-Identifier: MIT -->

# 中文扫描规则 (Chinese scan rules)

This table is the skill's standard for what counts as AI flavour: the agent works from these rows
when judging a mark, and the scanner reads the same rows to produce the marks. No pattern lives in
Python.

- **Kind** — `ban` (rewrite on sight), `review` (judge against the article's purpose), `family`
  (count evidence only), or `opener:<group>` (sentence-initial connective density).
- **Pattern** — a Python regex, matched case-insensitively **inside one sentence**. Escape `|` as
  `\|` because the row is a Markdown table. Rows sharing a rule key are alternatives of one family.
- **Probe** — a sentence the pattern must match. The regression suite fails when a rule has no probe
  or a probe stops matching, so a typo cannot silently disable a rule. `-` means the probe is given on
  another row of the same key.
- **Model** — the model family the row is characteristic of, or `-` for language-generic behaviour.
  A model name is a style profile, never an authorship claim.
- **Source** — `W` [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing);
  `K` [Kobak et al. 2025, excess vocabulary](https://arxiv.org/abs/2406.07016);
  `G` [Graphite AI-tells corpus](https://graphite.io/five-percent/research/ai-tells);
  `C` community field work ([feedsquad](https://feedsquad.com/ai-tells), [tropes.fyi](https://tropes.fyi/),
  [claudisms.ai](https://claudisms.ai/), [ANTI-SLOP](https://github.com/NousResearch/autonovel/blob/master/ANTI-SLOP.md),
  Reddit and Hacker News threads); `V` vendor guidance (OpenAI model guides, Anthropic system-prompt
  release notes); `Z` Chinese-language community reporting; `-` this skill owner's own preference.

**有争议或取决于体例的痕迹——只报告，不强制。** 中文破折号按每千字计：DeepSeek 5.16、Claude 4.25、
Gemini 0.51，人类写手 0.80 —— 因此它既不能证明也不能排除什么。问句小标题与序数小标题（一、二、三）
按文体判断，正式技术文档可以整篇不用。弯引号是部分模型的习惯（ChatGPT、DeepSeek 用，Gemini、Claude
不用），且容易被编辑器与系统智能引号掩盖。词表随模型代际轮换（delve 是 2023 年的标志，现已退潮），
"没出现"不等于"不是 AI 写的"。

**没有任何一行能覆盖的读校项。** 有些习惯不共用词面，正则和 n-gram 都发现不了，扫描之后必须通读：

- **写作动作播报** —— 文章在讲"我们接下来怎么看"（我们先看／顺着往下看／值得展开／我比较想沿着第三行继续看），而不是在讲事实。**第一人称观察是另一回事，要保留**（我们测量／我们尚未复现／从我们的角度看）。
- **问句式小标题** —— 小标题在提问（"已有方案解决到了哪里"）而不是陈述；`metrics.wh_heading` 给出计数。
- **每节同构收尾** —— 每一节都以同一种总结句收尾，只是换了词。
- **替读者下情绪判断** —— "这个安排会让人稍微停一下""值得注意"之类，用反应替代事实。
- **边界否定** —— 不属于／未验证／不得／不代表 携带范围信息，逐字保留；去否定只针对自我描述与营销语。

| Rule key | Kind | Label | Pattern | Probe | Model | Source | Advice |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zh-false-reversal | ban | Not-X-but-Y reversal | `不(?:是\|只(?:是)?\|仅(?:仅)?是)[^。！？!?；;\n]{0,90}?(?:而是\|更是\|而在\|在于)` | 这不是速度问题，而是延迟问题。 | DeepSeek V4 / generic | Z | State the actual mechanism or difference; drop the invented either/or framing. |
| zh-false-reversal | ban | Not-X-but-Y reversal | `真正[^。！？!?；;\n]{0,90}?不在[^。！？!?；;\n]{0,90}?(?:而在\|在于)` | - | DeepSeek V4 / generic | Z | State the actual mechanism or difference; drop the invented either/or framing. |
| zh-false-reversal | ban | Not-X-but-Y reversal | `不是靠` | - | DeepSeek V4 / generic | Z | State the actual mechanism or difference; drop the invented either/or framing. |
| zh-announce-answer | ban | Pre-announced verdict | `(?:先\|直接)(?:给出?\|说\|讲\|谈)(?:一[个句]\|一下)?(?:我(?:自己)?的)?(?:结论\|答案)` | 先给一个结论：缓存是瓶颈。 | - | Z | Enter from the fact or the question; put a supported judgement after its evidence. |
| zh-announce-answer | ban | Pre-announced verdict | `先把结论(?:放\|摆\|写)` | - | - | Z | Enter from the fact or the question; put a supported judgement after its evidence. |
| zh-teach-reader | ban | Reader instruction | `先把问题看清楚` | 先把问题看清楚，再决定改哪里。 | - | - | Explain the mechanism directly; delete instructions about how to read. |
| zh-teach-reader | ban | Reader instruction | `先(?:弄\|搞)明白一件事` | - | - | - | Explain the mechanism directly; delete instructions about how to read. |
| zh-teach-reader | ban | Reader instruction | `理解这一点[^。！？!?；;\n]{0,90}?才能` | - | - | - | Explain the mechanism directly; delete instructions about how to read. |
| zh-dramatic-scale | ban | Manufactured scale shock | `读入[与和、]生成[^。！？!?；;\n]{0,90}?差了?两个数量级` | 读入和生成差了两个数量级。 | - | - | Express the difference with the real workload, number, and conditions. |
| zh-burden-metaphor | ban | Personified burden hand-off | `(?:没了\|拿掉了\|消失了)[^。！？!?；;\n]{0,90}?(?:得\|要\|必须)自己(?:扛\|解决\|承担)` | 边界没了，同步得自己扛。 | - | - | Name the executing unit, the data dependency, or the resource constraint. |
| zh-burden-metaphor | ban | Personified burden hand-off | `中间商被踢掉` | - | - | - | Name the executing unit, the data dependency, or the resource constraint. |
| zh-burden-metaphor | ban | Personified burden hand-off | `同步得自己扛` | - | - | - | Name the executing unit, the data dependency, or the resource constraint. |
| zh-dramatic-priority | ban | Abstract runs-out-first | `(?:空间\|时间\|边界\|收益)比[^。！？!?；;\n]{0,90}?更早(?:见底\|耗尽\|到来)` | 空间比时间更早见底。 | - | - | Replace with a conditional comparison of a named resource or duration. |
| zh-empty-calculation | ban | Vague reckoning | `别算不该算的` | - | - | - | Say which computation was skipped or included. |
| zh-empty-calculation | ban | Vague reckoning | `该算什么[^。！？!?；;\n]{0,90}?不该算什么` | 别的该算什么、不该算什么。 | - | - | Say which computation was skipped or included. |
| zh-empty-gain | ban | Gain without an object | `[划画]的是什么[^。！？!?；;\n]{0,90}?收益的是什么` | 划的是什么，收益的是什么。 | - | - | Name the plotted metric or the concrete gain. |
| zh-forced-convergence | ban | Forced convergence | `取舍[^。！？!?；;\n]{0,90}?落到一个问题` | 取舍最后落到一个问题：先改哪里。 | - | - | Keep the individual decisions and their grounds. |
| zh-forced-convergence | ban | Forced convergence | `所有问题[^。！？!?；;\n]{0,90}?(?:归结\|归根\|落到)` | - | - | - | Keep the individual decisions and their grounds. |
| zh-value-verdict | ban | Value verdict for the reader | `真正做对的(?:事\|东西)` | 他们真正做对的事情是保持简单。 | - | - | Report behaviour and results; delete the verdict about what matters. |
| zh-value-verdict | ban | Value verdict for the reader | `真正值得(?:关注\|拿走\|带走)` | - | - | - | Report behaviour and results; delete the verdict about what matters. |
| zh-value-verdict | ban | Value verdict for the reader | `这件事(?:情)?真的值得[^。！？!?；;\n]{0,90}?拿` | - | - | - | Report behaviour and results; delete the verdict about what matters. |
| zh-role-slogan | ban | Symmetric role slogan | `你负责定[^。！？!?；;\n]{0,90}?[他它]负责定` | 你负责定方向，他负责定边界。 | - | - | Show who did what from the record instead of a slogan about division of labour. |
| zh-role-slogan | ban | Symmetric role slogan | `人(?:类)?定方向[^。！？!?；;\n]{0,90}?AI\s*负责穷举` | - | - | - | Show who did what from the record instead of a slogan about division of labour. |
| zh-one-line-moral | ban | One-line moral | `(?:如果\|若)?只留一句话` | 如果只留一句话，那就是先测再改。 | DeepSeek V4 | Z | Stop at the last informative result or question. |
| zh-one-line-moral | ban | One-line moral | `用一句话(?:概括\|总结)` | - | DeepSeek V4 | Z | Stop at the last informative result or question. |
| zh-one-line-moral | ban | One-line moral | `这才是[^。！？!?；;\n]{0,90}?最实在的含义` | - | DeepSeek V4 | Z | Stop at the last informative result or question. |
| zh-editor-leak | ban | Editing-process leak | `(?:原稿\|原文\|之前的说法)[^。！？!?；;\n]{0,90}?(?:写成\|不够准确\|有误\|混淆)` | 原稿把这件事写成了一次替换。 | - | - | Delete editing instructions; write any useful fact into the sentence it belongs to. |
| zh-editor-leak | ban | Editing-process leak | `不能写成` | - | - | - | Delete editing instructions; write any useful fact into the sentence it belongs to. |
| zh-editor-leak | ban | Editing-process leak | `(?:这里\|这两个东西).{0,16}(?:需要区分\|应分别描述\|需要描述成)` | - | - | - | Delete editing instructions; write any useful fact into the sentence it belongs to. |
| zh-editor-leak | ban | Editing-process leak | `(?:后面\|后文\|全文)统一使用` | - | - | - | Delete editing instructions; write any useful fact into the sentence it belongs to. |
| zh-editor-leak | ban | Editing-process leak | `按照你的要求` | - | - | - | Delete editing instructions; write any useful fact into the sentence it belongs to. |
| zh-editor-leak | ban | Editing-process leak | `这一段需要强调` | - | - | - | Delete editing instructions; write any useful fact into the sentence it belongs to. |
| zh-editor-leak | ban | Editing-process leak | `下面按[^。！？!?；;\n]{0,90}?重写` | - | - | - | Delete editing instructions; write any useful fact into the sentence it belongs to. |
| zh-editor-leak | ban | Editing-process leak | `本文依据[^。！？!?；;\n]{0,90}?原稿[^。！？!?；;\n]{0,90}?重写` | - | - | - | Delete editing instructions; write any useful fact into the sentence it belongs to. |
| zh-editor-leak | ban | Editing-process leak | `这句话容易让读者误解` | - | - | - | Delete editing instructions; write any useful fact into the sentence it belongs to. |
| zh-editor-leak | ban | Editing-process leak | `这些边界必须说清楚` | - | - | - | Delete editing instructions; write any useful fact into the sentence it belongs to. |
| zh-process-narration | review | 写作动作播报 | `^(?:于是\|所以\|那么\|因此\|接下来\|下面\|然后)?[，,]?(?:我们\|我)?(?:先\|再\|接着\|继续\|顺着\|沿着\|接下来\|下面\|后面\|然后\|可以\|想\|会\|要)[^。！？]{0,24}(?:看\|讲\|说\|谈\|理解\|分析\|展开\|追\|梳理\|连接)` | 我们先从一个编程 Agent 的工作过程讲起。 | - | - | 把"我们接下来怎么看"改成直接陈述。作者的第一人称观察保留（我们测量／我们尚未复现／从我们的角度看）。 |
| zh-corporate-jargon | review | 企业黑话 Corporate jargon | `(?:收口\|口径\|闭环\|抓手\|赋能\|颗粒度\|打通\|沉淀)` | 这个项目要先打通数据链路，形成闭环，再统一口径收口。 | - | - | 换成具体动词：赋能→支持，抓手→手段，颗粒度→细度，打通→连接，沉淀→积累，闭环→完整流程，口径→统计标准，收口→归总。若它确实是本文的精确术语（统计口径、数据颗粒度、控制闭环）就保留；同一篇里出现两次以上，或只是装饰性口号，就是口癖。 |
| zh-corporate-jargon | review | 企业黑话 Corporate jargon | `(?:对齐\|拉通\|心智\|打法\|复盘\|组合拳\|飞轮\|护城河\|降本增效\|数智化)` | 先拉通各团队对齐心智，再复盘打法。 | - | - | 换成具体说法：对齐→核对／与…一致，拉通→协调，心智→认知，打法→做法，复盘→回顾，组合拳→一组措施，飞轮→正反馈循环，护城河→优势，降本增效→降低成本，数智化→数字化。技术义保留：内存对齐、指令对齐、故障复盘。 |
| zh-chatbot-voice | ban | 对话残留与身份声明 | `(?:作为\|身为)(?:一个\|一名)?\s*(?:AI\|人工智能\|大语言模型\|语言模型\|智能助手)` | 作为一个 AI，希望这对你有帮助。 | - | Z | 删除对话残留与身份声明；只保留文稿本身要表达的内容。 |
| zh-chatbot-voice | ban | 对话残留与身份声明 | `我是(?:一个)?\s*(?:AI\|人工智能\|Claude\|GPT\|ChatGPT\|Gemini\|DeepSeek\|Kimi\|GLM\|Qwen\|豆包\|文心)` | - | - | Z | 删除对话残留与身份声明；只保留文稿本身要表达的内容。 |
| zh-chatbot-voice | ban | 对话残留与身份声明 | `(?:希望\|但愿)(?:这\|上述\|以上\|我的回答)?(?:些\|个)?(?:内容\|回答)?对(?:你\|您)(?:有所\|有)?帮助` | - | - | Z | 删除对话残留与身份声明；只保留文稿本身要表达的内容。 |
| zh-chatbot-voice | ban | 对话残留与身份声明 | `(?:如果\|若)(?:你\|您)(?:还)?(?:有\|需要)(?:其他\|其它\|任何)?(?:问题\|疑问\|需要)` | - | - | Z | 删除对话残留与身份声明；只保留文稿本身要表达的内容。 |
| zh-chatbot-voice | ban | 对话残留与身份声明 | `如需(?:进一步\|更多\|其他)(?:帮助\|了解\|信息\|支持)` | - | - | Z | 删除对话残留与身份声明；只保留文稿本身要表达的内容。 |
| zh-chatbot-voice | ban | 对话残留与身份声明 | `(?:我\|本人)(?:可以\|会\|将)(?:继续\|帮你\|为您\|为你\|进一步)(?:解答\|说明\|分析\|梳理)` | - | - | Z | 删除对话残留与身份声明；只保留文稿本身要表达的内容。 |
| zh-chatbot-voice | ban | 对话残留与身份声明 | `(?:很)?高兴(?:为\|能\|为你\|为您)?(?:你\|您)?(?:解答\|回答\|服务)` | - | - | Z | 删除对话残留与身份声明；只保留文稿本身要表达的内容。 |
| zh-chatbot-voice | ban | 对话残留与身份声明 | `以下(?:是\|为)我(?:的\|对.{0,10}的)(?:回答\|理解\|分析)` | - | - | Z | 删除对话残留与身份声明；只保留文稿本身要表达的内容。 |
| zh-defensive-correction | review | Defensive correction | `不能(?:直接)?(?:理解为\|换算成\|据此认定)` | 不能直接理解为硬件上限。 | - | - | Check whether it answers an objection from the chat; keep the necessary condition, drop the defence. |
| zh-defensive-correction | review | Defensive correction | `材料不足以支持` | - | - | - | Check whether it answers an objection from the chat; keep the necessary condition, drop the defence. |
| zh-defensive-correction | review | Defensive correction | `(?:应该\|需要\|应当)分别(?:描述\|表述\|测量)` | - | - | - | Check whether it answers an objection from the chat; keep the necessary condition, drop the defence. |
| zh-reminder | family | Reader reminder | `(?:这里\|在此)(?:还\|也)?(?:要\|需要\|必须)(?:说明\|强调\|提醒\|区分)` | 这里还需要说明一点。 | - | Z | Move the condition into the factual sentence and merge repeated reminders. |
| zh-reminder | family | Reader reminder | `(?:需要\|值得)(?:特别)?注意` | - | - | Z | Move the condition into the factual sentence and merge repeated reminders. |
| zh-reminder | family | Reader reminder | `补一句必要的克制` | - | - | Z | Move the condition into the factual sentence and merge repeated reminders. |
| zh-concession | family | Concession then reversal | `(?:虽然\|尽管\|即使\|纵然)[^。！？!?；;\n]{0,90}?(?:但是\|但\|却\|仍然\|仍旧\|还是)` | 虽然局部变慢，但整体更快。 | - | - | Check whether consecutive paragraphs all set up the same concession and reversal. |
| zh-escalation | family | Escalating addition | `(?:不仅\|不光\|不止)[^。！？!?；;\n]{0,90}?(?:而且\|还\|更\|也)` | 不仅更快，而且更省内存。 | - | - | Reduce repeated escalation; list the related facts in one place. |
| zh-escalation | family | Escalating addition | `既[^。！？!?；;\n]{0,90}?又` | - | - | - | Reduce repeated escalation; list the related facts in one place. |
| zh-exclusive-condition | family | Exclusive condition | `只有[^。！？!?；;\n]{0,90}?才` | 只有写入完成，才能读取。 | - | - | Check whether the condition is necessary or merely prominent, and whether it repeats across sections. |
| zh-exclusive-condition | family | Exclusive condition | `只要[^。！？!?；;\n]{0,90}?就` | - | - | - | Check whether the condition is necessary or merely prominent, and whether it repeats across sections. |
| zh-exclusive-condition | family | Exclusive condition | `唯有[^。！？!?；;\n]{0,90}?才` | - | - | - | Check whether the condition is necessary or merely prominent, and whether it repeats across sections. |
| zh-correlation | family | The more, the more | `越[^。！？!?；;\n，,]{1,35}[，,]?[^。！？!?；;\n]{0,15}越` | 缓存越大，命中率越高。 | - | - | Use a measurement or explicit cause; avoid repeating the same crescendo. |
| zh-choice | family | Either-or preference | `与其[^。！？!?；;\n]{0,90}?不如` | 与其加缓存，不如先测延迟。 | - | - | Restore the choice and its evidence; avoid repeated binary framings. |
| zh-choice | family | Either-or preference | `宁可[^。！？!?；;\n]{0,90}?也不` | - | - | - | Restore the choice and its evidence; avoid repeated binary framings. |
| zh-paired-contrast | family | Paired contrast | `一方面[^。！？!?；;\n]{0,90}?另一方面` | 一方面要快，另一方面要稳。 | - | - | Check for deliberate local parallelism; do not copy it across sections. |
| zh-paired-contrast | family | Paired contrast | `一边[^。！？!?；;\n]{0,90}?一边` | - | - | - | Check for deliberate local parallelism; do not copy it across sections. |
| zh-paired-contrast | family | Paired contrast | `有的[^。！？!?；;\n]{0,90}?有的` | - | - | - | Check for deliberate local parallelism; do not copy it across sections. |
| zh-cause-emphasis | family | Emphatic causation | `之所以[^。！？!?；;\n]{0,90}?是因为` | 之所以变慢，是因为锁竞争。 | - | - | Keep the causal link; reduce repeated emphasis. |
| zh-cause-emphasis | family | Emphatic causation | `正(?:是)?因为[^。！？!?；;\n]{0,90}?(?:所以\|才)` | - | - | - | Keep the causal link; reduce repeated emphasis. |
| zh-meaning-summary | family | Section-end meaning summary | `^(?:这\|上述结果\|这些结果)(?:也\|就\|恰恰)?(?:说明\|意味着\|证明\|表明)` | 这说明批量大小影响吞吐。 | - | Z | Check whether the summary adds information or repeats the section. |
| zh-meaning-summary | family | Section-end meaning summary | `^(?:由此可见\|归根结底\|说到底\|本质上\|综上所述\|总而言之)` | - | - | Z | Check whether the summary adds information or repeats the section. |
| zh-why-question | family | Rhetorical why-question | `为什么[^。！？!?；;\n]{0,90}?[？?]` | 为什么是他们先做出来？ | - | - | Keep genuine research questions; delete questions used only to structure the text. |
| zh-why-question | family | Rhetorical why-question | `为什么(?:是他们\|愿意开源\|只用了)` | - | - | - | Keep genuine research questions; delete questions used only to structure the text. |
| zh-ordinal-sequence | family | 序数词铺陈 | `(?:首先\|其次\|再次\|再者\|其一\|其二\|其三)` | 首先确认需求，其次拆分任务。 | - | Z | 检查枚举是否必要；能直接叙述的，不必先编号再展开。 |
| zh-hype-vocabulary | review | Unsupported evaluation vocabulary | `(?:重塑\|引领\|革命性\|里程碑\|深度融合\|颠覆性)` | 这个方案能够重塑整个体系。 | - | Z | Evidence-based only: write the fact; delete the evaluation when nothing supports it. |
| zh-opener-turn | opener:turn | Turn opener | `^(?:不过\|然而\|但是\|但\|可是\|可见\|反过来)` | - | - | - | Sentence-initial connective; judge by density, never by a single use. |
| zh-opener-result | opener:result | Result opener | `^(?:因此\|所以\|因而\|于是)` | - | - | - | Sentence-initial connective; judge by density, never by a single use. |
| zh-opener-addition | opener:addition | Addition opener | `^(?:此外\|另外\|与此同时\|同时\|值得一提的是)` | - | - | - | Sentence-initial connective; judge by density, never by a single use. |
| zh-opener-condition | opener:condition | Condition opener | `^(?:如果\|假如\|倘若)` | - | - | - | Sentence-initial connective; judge by density, never by a single use. |
| zh-opener-explain | opener:explain | Explanation opener | `^(?:其实\|实际上\|换句话说\|也就是说\|说白了)` | - | - | - | Sentence-initial connective; judge by density, never by a single use. |
| zh-chatbot-voice | ban | 对话残留与身份声明 | (?:问得好\|这个问题问得(?:好\|很好)\|说得好\|你说得对\|非常好的问题) | 问得好，这个问题确实值得拆开看。 | Kimi K3 | Z | 删除对话残留、奉承开场与身份声明；只保留文稿本身要表达的内容。 |
| zh-hype-vocabulary | review | Unsupported evaluation vocabulary | `(?:底层逻辑\|顶层设计)` | 从底层逻辑看，这其实是一个状态机问题。 | Gemini 3.x | Z | Evidence-based only: write the fact; delete the evaluation when nothing supports it. |
| zh-parenthetical-append | family | 句末括号补语 | （[^）\n]{6,}）\s*[。！？]?$ | 他把条件和数据都塞进了句末（包括采样窗口与批次大小）。 | DeepSeek V4 | Z | 把括号里的条件写进句子本身，或另起一句；不要用括号堆数据。 |
| zh-glm-cot-switch | ban | 思考链中英混排 | [让请]\s*me\b | 好，让 me 再看一下这个函数。 | GLM-5.x | Z | 删除过程播报与中英混排的思考痕迹。 |
| zh-grok-cyrillic | review | 中文里混入西里尔字母 | [\u0400-\u04ff] | 这个方案好是好，只是差点什么（печат）。 | Grok 4.x | Z | 核对是否为无意的外语残留；是则删除。 |
| zh-deepseek-closer | review | 短句收束 | (?:这\|那)就够了 | 缓存命中率提升，这就够了。 | DeepSeek V4 | Z | 检查这句是否只是收束口号；有信息就并入上一句。 |
