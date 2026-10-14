# 会后方向导读

ICML · 2024

在这组 ICML 2024 的 20 篇样本中，四篇工作与 Transformer/LLM 高效推理直接相关，分别关注低比特表示、注意力计算和外部工具交互时的资源利用。优先阅读 FrameQuant 与 CHAI，再按自己的部署瓶颈查看另外两篇。

已评估 20/20 篇 · 相关 4 篇 · 待核查 0 篇 · 未处理 0 篇。

[搜索与筛选](index.html) · [论文目录](papers.csv) · [完整记录](results.json)

本次覆盖范围尚未确认完整；下方结果对应已取得的论文资料。

## 研究方向

- 以量化降低 Transformer/大语言模型推理的计算与内存成本
- 以高效注意力降低 Transformer/大语言模型推理的计算与内存成本
- 以推理系统降低 Transformer/大语言模型推理的计算与内存成本

## 方向导读

### 以量化降低 Transformer/大语言模型推理的计算与内存成本

FrameQuant 在 Fusion Frame 表示中进行低比特量化。阅读时重点核查额外表示开销、精度变化，以及目标硬件上的实际推理收益。

依据：[FrameQuant: Flexible Low\-Bit Quantization for Transformers](<https://proceedings.mlr.press/v235/adepu24a.html>)

### 以高效注意力降低 Transformer/大语言模型推理的计算与内存成本

CHAI 利用运行时注意力头相关性减少冗余；LeaPformer 用动态比例重加权，使线性化 Transformer 适用于目标长度未知的自回归任务。两者分别适合检查运行时缓存与注意力结构的成本。

依据：[CHAI: Clustered Head Attention for Efficient LLM Inference](<https://proceedings.mlr.press/v235/agarwal24a.html>)、[LeaPformer: Enabling Linear Transformers for Autoregressive and Simultaneous Tasks via Learned Proportions](<https://proceedings.mlr.press/v235/agostinelli-iii24a.html>)

### 以推理系统降低 Transformer/大语言模型推理的计算与内存成本

InferCept 处理外部工具交互造成的生成拦截和上下文重算。可重点阅读资源恢复策略、并发请求与外部调用时延对系统利用率的影响。

依据：[InferCept: Efficient Intercept Support for Augmented Large Language Model Inference](<https://proceedings.mlr.press/v235/abhyankar24a.html>)


## 优先阅读（2 篇）

| ID | 论文 | 关联 | 推荐理由 |
|---|---|---|---|
| [P-A4B6E56A62B6](index.html#P-A4B6E56A62B6) | [FrameQuant: Flexible Low\-Bit Quantization for Transformers](<https://proceedings.mlr.press/v235/adepu24a.html>) | 直接相关 | FrameQuant明确以Transformer服务的计算和内存成本为问题，采用训练后量化，并在Fusion Frame表示中进行近两比特量化。 |
| [P-07B46CD2B3FA](index.html#P-07B46CD2B3FA) | [CHAI: Clustered Head Attention for Efficient LLM Inference](<https://proceedings.mlr.press/v235/agarwal24a.html>) | 直接相关 | CHAI识别LLM注意力头之间的相关冗余，在运行时合并头，明确同时降低attention计算与KV cache内存，直接匹配高效推理问题。 |

## 完整相关目录

### 以量化降低 Transformer/大语言模型推理的计算与内存成本

- [P-A4B6E56A62B6](index.html#P-A4B6E56A62B6) · [FrameQuant: Flexible Low\-Bit Quantization for Transformers](<https://proceedings.mlr.press/v235/adepu24a.html>)

### 以高效注意力降低 Transformer/大语言模型推理的计算与内存成本

- [P-07B46CD2B3FA](index.html#P-07B46CD2B3FA) · [CHAI: Clustered Head Attention for Efficient LLM Inference](<https://proceedings.mlr.press/v235/agarwal24a.html>)
- [P-0E78607BC365](index.html#P-0E78607BC365) · [LeaPformer: Enabling Linear Transformers for Autoregressive and Simultaneous Tasks via Learned Proportions](<https://proceedings.mlr.press/v235/agostinelli-iii24a.html>)

### 以推理系统降低 Transformer/大语言模型推理的计算与内存成本

- [P-24C19D3E6FE8](index.html#P-24C19D3E6FE8) · [InferCept: Efficient Intercept Support for Augmented Large Language Model Inference](<https://proceedings.mlr.press/v235/abhyankar24a.html>)


## 阅读建议与依据

### P-A4B6E56A62B6 · FrameQuant: Flexible Low\-Bit Quantization for Transformers

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

### P-07B46CD2B3FA · CHAI: Clustered Head Attention for Efficient LLM Inference

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

### P-24C19D3E6FE8 · InferCept: Efficient Intercept Support for Augmented Large Language Model Inference

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

### P-0E78607BC365 · LeaPformer: Enabling Linear Transformers for Autoregressive and Simultaneous Tasks via Learned Proportions

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

## 范围与来源

Scope: PMLR volume 235 only\. Parsed 2610 unique paper links from 2610 list records; retrieved 20 detail records\. track=main denotes this conference proceedings volume, not verified technical subtracks\. Other volumes, workshops, late updates and on\-site attendance are not covered; list parsing alone does not prove coverage of the entire conference\. \-\-limit 20: first\-N sample in official list order; not a full\-conference relevance sample\.

缺少摘要 0 篇；已排除 16 篇。待核查、排除和未处理记录可在 HTML 按状态查看，完整判断保存在 JSON 中。

[官方论文列表](<https://proceedings.mlr.press/v235/>)

资料获取时间：2026\-10\-14T14:54:57\.936188\+00:00
