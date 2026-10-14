# 参会阅读清单

会议：International Conference on Machine Learning；年份：2024；范围：main。

[论文列表来源](<https://proceedings.mlr.press/v235/>)

获取日期：2026\-10\-14T14:54:57\.936188\+00:00

## 覆盖情况

输入 20 篇；已评估 20 篇；推荐 4 篇；排除 16 篇；待核查 0 篇；未处理 0 篇。

缺少摘要 0 篇；仅有标题资料 0 篇；录用状态未知 0 篇；合并重复记录 0 条。

范围状态：unknown。Scope: PMLR volume 235 only\. Parsed 2610 unique paper links from 2610 list records; retrieved 20 detail records\. track=main denotes this conference proceedings volume, not verified technical subtracks\. Other volumes, workshops, late updates and on\-site attendance are not covered; list parsing alone does not prove coverage of the entire conference\. \-\-limit 20: first\-N sample in official list order; not a full\-conference relevance sample\.

覆盖尚未确认完整；清单仅反映已处理且有证据的论文。

## 研究兴趣

- quant：以量化降低 Transformer/大语言模型推理的计算与内存成本（主要）
  - 用户输入：我想了解所给 ICML 2024 样本中降低 Transformer/大语言模型推理计算与内存成本的论文，关注量化、注意力计算和推理系统；仅优化训练、没有推理价值的工作暂不关注。请生成参会精选（最多2篇）和会后方向总结。
- attention：以高效注意力降低 Transformer/大语言模型推理的计算与内存成本（主要）
  - 用户输入：我想了解所给 ICML 2024 样本中降低 Transformer/大语言模型推理计算与内存成本的论文，关注量化、注意力计算和推理系统；仅优化训练、没有推理价值的工作暂不关注。请生成参会精选（最多2篇）和会后方向总结。
- systems：以推理系统降低 Transformer/大语言模型推理的计算与内存成本（主要）
  - 用户输入：我想了解所给 ICML 2024 样本中降低 Transformer/大语言模型推理计算与内存成本的论文，关注量化、注意力计算和推理系统；仅优化训练、没有推理价值的工作暂不关注。请生成参会精选（最多2篇）和会后方向总结。

## 优先阅读（最多 2 篇）

1. [FrameQuant: Flexible Low\-Bit Quantization for Transformers](<https://proceedings.mlr.press/v235/adepu24a.html>) — 优先级 1；直接相关；pmlr:235:adepu24a
2. [CHAI: Clustered Head Attention for Efficient LLM Inference](<https://proceedings.mlr.press/v235/agarwal24a.html>) — 优先级 1；直接相关；pmlr:235:agarwal24a
## 推荐依据

### FrameQuant: Flexible Low\-Bit Quantization for Transformers

[论文](<https://proceedings.mlr.press/v235/adepu24a.html>) · ID：pmlr:235:adepu24a · [PDF](<https://raw.githubusercontent.com/mlresearch/v235/main/assets/adepu24a/adepu24a.pdf>)

作者：Harshavardhan Adepu、Zhanpeng Zeng、Li Zhang、Vikas Singh

优先级：1；相关性：高；关联：直接相关；证据：充分。

匹配方向：以量化降低 Transformer/大语言模型推理的计算与内存成本

推荐理由：FrameQuant明确以Transformer服务的计算和内存成本为问题，采用训练后量化，并在Fusion Frame表示中进行近两比特量化。与用户的量化和部署效率兴趣直接匹配。

重点阅读：优先阅读Fusion Frame表示与量化过程，检查额外表示开销、精度损失和部署时算子实现；重点区分模型压缩、显存节约与真实推理加速。

来源证据：

- “quantize Transformer\-based models to just two bits \(plus some overhead\)” — [Abstract](<https://proceedings.mlr.press/v235/adepu24a.html>)（abstract）

关键差异：

- 通过低比特参数表示减少开销，与CHAI在运行时减少attention头的冗余不同。
- 摘要明确保留额外开销，不能将两比特直接当作实际端到端内存比例。

待核查项：

- 仅阅读摘要；实际额外存储、算子开销和端到端延迟尚需正文核对。
- 不同Transformer任务和大规模LLM中的精度权衡尚未核对。
- 现场展示、时间、地点和作者到场均未核实。

现场展示安排：尚无已确认日程。

### CHAI: Clustered Head Attention for Efficient LLM Inference

[论文](<https://proceedings.mlr.press/v235/agarwal24a.html>) · ID：pmlr:235:agarwal24a · [PDF](<https://raw.githubusercontent.com/mlresearch/v235/main/assets/agarwal24a/agarwal24a.pdf>)

作者：Saurabh Agarwal、Bilge Acun、Basil Hosmer、Mostafa Elhoushi、Yejin Lee、Shivaram Venkataraman、Dimitris Papailiopoulos、Carole\-Jean Wu

优先级：1；相关性：高；关联：直接相关；证据：充分。

匹配方向：以高效注意力降低 Transformer/大语言模型推理的计算与内存成本

推荐理由：CHAI识别LLM注意力头之间的相关冗余，在运行时合并头，明确同时降低attention计算与KV cache内存，直接匹配高效推理问题。

重点阅读：优先阅读头相关性估计、运行时聚类及KV cache组织；核查额外聚类成本、输入长度与批量变化，以及各模型精度和延迟测量。

来源证据：

- “correlation for self\-attention at runtime, thus reducing both memory and compute\.” — [Abstract](<https://proceedings.mlr.press/v235/agarwal24a.html>)（abstract）

关键差异：

- 以运行时注意力冗余为切入点，不要求先微调；与FrameQuant的参数表示压缩和LeaPformer的线性attention设计不同。

待核查项：

- 仅阅读摘要；报告的缓存和延迟收益尚未核对正文实验条件。
- 不同序列长度和负载下的聚类成本及精度变化仍待核查。
- 现场展示、时间、地点和作者到场均未核实。

现场展示安排：尚无已确认日程。

## 待核查与未处理

无。

已排除 16 篇；逐篇理由与原文证据保存在本次 assessments 文件中。

## 精选取舍与交流问题

本次两篇精选分别覆盖低比特量化与运行时注意力计算；InferCept与LeaPformer保留在会后报告的四篇相关全表。优先级反映本次阅读次序，未根据摘要评定论文质量。

- **FrameQuant**：Fusion Frame表示和额外元数据的实际存储开销是多少？在目标硬件上，近两比特表示与现有量化算子如何结合，精度变化和端到端推理延迟如何测量？问题来自摘要中“plus some overhead”和Fusion Frame量化机制。[摘要来源](https://proceedings.mlr.press/v235/adepu24a.html)
- **CHAI**：运行时头聚类的额外计算如何计入延迟？不同输入长度与batch下，KV cache节约和头相关性是否稳定？问题来自摘要的运行时合并与缓存成本目标。[摘要来源](https://proceedings.mlr.press/v235/agarwal24a.html)

这两篇的现场展示、时间、地点和会议当地日程时区均未核实，本清单用于安排阅读与准备交流问题，尚不能作为现场路线。

## 本次资料边界

原始资料仅为用户给定的`tests/fixtures/icml2024-pmlr-sample.json`。论文链接、PMLR来源日期和accepted标签沿用该样本；本次离线检查了会议与年份元数据、论文身份、全样本覆盖和逐条摘要引用。四篇推荐的“证据充分”指足以支持主题关联判断；实际方法实现、实验比较与端到端收益需要正文。PDF链接供后续阅读，本次未读取正文。
