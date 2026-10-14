# 会后方向论文清单

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

## 各方向相关论文全表

### 以量化降低 Transformer/大语言模型推理的计算与内存成本

- [FrameQuant: Flexible Low\-Bit Quantization for Transformers](<https://proceedings.mlr.press/v235/adepu24a.html>)（pmlr:235:adepu24a；直接相关）

### 以高效注意力降低 Transformer/大语言模型推理的计算与内存成本

- [CHAI: Clustered Head Attention for Efficient LLM Inference](<https://proceedings.mlr.press/v235/agarwal24a.html>)（pmlr:235:agarwal24a；直接相关）
- [LeaPformer: Enabling Linear Transformers for Autoregressive and Simultaneous Tasks via Learned Proportions](<https://proceedings.mlr.press/v235/agostinelli-iii24a.html>)（pmlr:235:agostinelli\-iii24a；直接相关）

### 以推理系统降低 Transformer/大语言模型推理的计算与内存成本

- [InferCept: Efficient Intercept Support for Augmented Large Language Model Inference](<https://proceedings.mlr.press/v235/abhyankar24a.html>)（pmlr:235:abhyankar24a；直接相关）

## 样本中的方向总结

以下比较来自四篇摘要的问题定义与方法描述。

| 子方向 | 观察到的切入点 | 重点阅读问题 |
|---|---|---|
| 低比特量化 | FrameQuant在Fusion Frame表示中量化Transformer参数，摘要给出近两比特加额外开销的方案。[FrameQuant](https://proceedings.mlr.press/v235/adepu24a.html) | 表示开销如何计入实际占用，目标硬件能否得到端到端收益？ |
| 注意力计算 | CHAI在运行时合并高相关注意力头；LeaPformer用动态比例重加权，使线性化Transformer适用于目标长度未知的自回归任务。[CHAI](https://proceedings.mlr.press/v235/agarwal24a.html)、[LeaPformer](https://proceedings.mlr.press/v235/agostinelli-iii24a.html) | 前者检查聚类成本与KV cache组织，后者检查增量计算状态与自回归推理评测。 |
| 推理系统 | InferCept处理工具或外部环境交互引起的生成拦截，减少已计算上下文的重算，并将节约内存用于更多请求。[InferCept](https://proceedings.mlr.press/v235/abhyankar24a.html) | 外部调用时延、恢复策略和并发请求如何影响资源利用？ |

四篇摘要分别定位参数表示、注意力算子与请求生命周期中的成本，因此阅读时可先确定自己的部署瓶颈，再选择相应机制。此分解是对摘要问题定义的综合，来源为[FrameQuant](https://proceedings.mlr.press/v235/adepu24a.html)、[CHAI](https://proceedings.mlr.press/v235/agarwal24a.html)、[LeaPformer](https://proceedings.mlr.press/v235/agostinelli-iii24a.html)和[InferCept](https://proceedings.mlr.press/v235/abhyankar24a.html)。样本没有这些方法联合使用的实验，组合收益仍需另行验证。

LeaPformer值得保留，因为摘要明确讨论线性化Transformer在自回归任务中的适用性，并包含自回归语言建模；新架构可能需要训练，但用户排除的是没有推理价值的训练优化。[LeaPformer](https://proceedings.mlr.press/v235/agostinelli-iii24a.html)

本次只观察PMLR官方顺序前20篇，不能据此判断整个ICML的热点分布、方法领先性或相对往年的增长；论文集的其他部分仍未纳入本次范围。

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

### InferCept: Efficient Intercept Support for Augmented Large Language Model Inference

[论文](<https://proceedings.mlr.press/v235/abhyankar24a.html>) · ID：pmlr:235:abhyankar24a · [PDF](<https://raw.githubusercontent.com/mlresearch/v235/main/assets/abhyankar24a/abhyankar24a.pdf>)

作者：Reyna Abhyankar、Zijian He、Vikranth Srivatsa、Hao Zhang、Yiying Zhang

优先级：2；相关性：高；关联：直接相关；证据：充分。

匹配方向：以推理系统降低 Transformer/大语言模型推理的计算与内存成本

推荐理由：工具或外部环境交互把LLM生成切成多个请求时，会重新计算已有上下文。InferCept针对截断和恢复过程减少GPU资源浪费，并把节约的内存用于服务更多请求，直接对应推理系统成本。

重点阅读：优先查阅生成拦截与恢复协议、上下文复用和GPU内存管理；随后核对外部调用时延、并发负载及吞吐实验设置。

来源证据：

- “InferCept minimizes the GPU resource waste caused by LLM interceptions and dedicates saved memory for serving more requests\.” — [Abstract](<https://proceedings.mlr.press/v235/abhyankar24a.html>)（abstract）

关键差异：

- 面向工具或代理增强的LLM，价值来自交互中断后的资源利用；与权重量化、注意力头合并对应不同开销。

待核查项：

- 仅阅读摘要；资源管理机制与吞吐结论尚未核对正文。
- 普通连续生成任务的收益尚不明确。
- 现场展示、时间、地点和作者到场均未核实。

### LeaPformer: Enabling Linear Transformers for Autoregressive and Simultaneous Tasks via Learned Proportions

[论文](<https://proceedings.mlr.press/v235/agostinelli-iii24a.html>) · ID：pmlr:235:agostinelli\-iii24a · [PDF](<https://raw.githubusercontent.com/mlresearch/v235/main/assets/agostinelli-iii24a/agostinelli-iii24a.pdf>)

作者：Victor Agostinelli Iii、Sanghyun Hong、Lizhong Chen

优先级：2；相关性：中；关联：直接相关；证据：充分。

匹配方向：以高效注意力降低 Transformer/大语言模型推理的计算与内存成本

推荐理由：LeaPformer解决线性化Transformer的重加权函数依赖目标序列长度，妨碍自回归与同步任务的问题。其动态比例机制使高效attention能用于长度未知的推理场景；摘要明确包含自回归语言建模验证。

重点阅读：优先查阅线性attention重加权及动态比例模块，检查自回归增量计算是否可缓存；核查吞吐指标的测量条件和部署相对标准Transformer的开销。

来源证据：

- “dynamic proportions derived via a compact module, enabling more flexible attention concentration patterns\.” — [Abstract](<https://proceedings.mlr.press/v235/agostinelli-iii24a.html>)（abstract）

关键差异：

- 属于attention架构设计，可在训练后服务自回归任务；用户排除的是没有推理价值的训练优化，并不排除需训练的新架构。
- 摘要中的语言建模规模不能外推为大规模LLM部署实测；与CHAI的运行时头合并不同。

待核查项：

- 仅阅读摘要；自回归实验中的推理吞吐和内存收益需正文核对。
- 大规模预训练LLM的适配、权重复用及硬件实现尚未确认。

## 待核查与未处理

无。

已排除 16 篇；逐篇理由与原文证据保存在本次 assessments 文件中。

## 本次资料边界

原始资料仅为用户给定的`tests/fixtures/icml2024-pmlr-sample.json`。论文链接、PMLR来源日期和accepted标签沿用该样本；本次离线检查了会议与年份元数据、论文身份、全样本覆盖和逐条摘要引用。四篇推荐的“证据充分”指足以支持主题关联判断；实际方法实现、实验比较与端到端收益需要正文。PDF链接供后续阅读，本次未读取正文。
