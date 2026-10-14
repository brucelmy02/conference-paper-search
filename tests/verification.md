# 第一版验证记录

日期：2026-10-14。

## 已验证

- 官方 skill 结构检查通过；UI metadata 为有效 UTF-8 YAML。
- `python -m unittest discover -s tests -v`：32 项测试全部通过。包括全量分批、去重冲突、录用状态、证据原文、跨 topic 边界、缺失资料、部分日程、报告数量限制和 CLI 流程。
- 实际从 PMLR ICML 2024 v235 获取官方列表前 20 篇：20 篇标题、作者、完整摘要均成功，详情失败 0。样本文件：`tests/fixtures/icml2024-pmlr-sample.json`。
- 独立执行者按“Transformer/LLM 推理计算与内存成本”建立兴趣并逐篇筛选：处理 20 篇，识别相关 4 篇，排除 16 篇，pending 与未处理均为 0。所有推荐证据通过原文片段核验。
- 四篇相关工作：FrameQuant、CHAI、InferCept、LeaPformer。参会示例精选前两篇，会后示例保留四篇全表并附有论文来源的比较。
- 参会报告的 top-k 约束已应用到展示的相关论文；排除原因默认保存于判断文件，详细审计可通过 `--include-excluded` 生成。

## 产物与复核

示例位于 examples/：attend-report.md、recap-report.md、sample-profile.json、sample-assessments.json、sample-validation.json。

```powershell
python skills/conference-paper-search/scripts/paper_pipeline.py validate --papers tests/fixtures/icml2024-pmlr-sample.json --profile examples/sample-profile.json --assessments examples/sample-assessments.json
```

脚本报告输出逐篇证据和分组，交流问题和跨论文综合由执行 skill 的 agent 基于材料补充。独立执行原始文件保留在 `.test-runs/forward-test/`，不混入 skill 安装包。

## 验证范围

这次是官方顺序前 20 篇的行为试跑，未建立完整会议的人工相关性标签，因此不报告全会议召回率或准确率。

自动获取仅对 PMLR 跑过实际网络验证。其他七个会议已提供核查过的官方来源路由，仍需按具体年份测试获取与范围适配。Scholar 论文提炼、上传论文提炼和反馈调整已有流程规则，尚未用真实作者身份及上传全文进行端到端评估。

资料仅覆盖摘要。相关性判断得到摘要支持，方法质量、硬件收益和实验比较仍需正文依据；现场日程未获取，示例不提供现场路线。
