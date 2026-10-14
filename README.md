# conference-paper-search

根据个人或课题组的研究兴趣，从 AI 会议官方论文列表中筛选相关论文，并给出可核查的推荐依据。

## 两种用途

| 模式 | 输出重点 |
|---|---|
| 参会清单 | 优先阅读的论文、匹配理由、交流问题，以及已核实的展示安排 |
| 会后总结 | 相关论文全表、子方向分组、代表工作之间的联系与差异 |

研究兴趣支持三种来源：用户直接描述、个人或导师近年论文、上传的代表论文。用户当前需求优先于从发表记录中推断出的方向，各方向保留来源依据。直接描述已有真实论文试跑；作者论文和上传论文的兴趣提炼已有流程规则，尚待真实端到端验证。

## 四份输出

每次任务统一导出以下文件，使用一致的论文 ID：

| 文件 | 用途 |
|---|---|
| `report.md` | 导读、阅读顺序、方向总结和逐篇推荐依据 |
| `papers.csv` | 全部相关及待核查论文，便于表格软件筛选和排序 |
| `results.json` | 完整论文资料、相关性判断、证据与覆盖统计 |
| `index.html` | 单文件本地页面，提供搜索、筛选、排序、详情和阅读标记 |

HTML 可离线打开；阅读标记保存在当前浏览器中，可手动导出。

## 安装与使用

需要支持 skill 的 AI agent。将本仓库的 `skills/conference-paper-search/` 整个目录复制到目标工具支持的 skill 目录。Codex 本机通常使用 `~/.codex/skills/conference-paper-search/`；其他客户端按各自的安装方式处理。

辅助脚本需要 Python 3.10+，仅使用标准库，无需安装额外 Python 包。资料理解和相关性判断由执行 skill 的 agent 完成，脚本负责获取、整理、验证与导出，无需另外配置模型 API。

示例请求：

```text
$conference-paper-search 筛选 ICML 2024 中降低 Transformer/LLM 推理计算和内存成本的论文，重点关注量化、注意力计算和推理系统；暂不关注只有训练收益的工作。生成会后总结和四份输出。
```

也可以提供准确的作者主页链接，或上传代表论文并说明关注其中的问题、方法或应用场景。会议、年份和 track 决定本次筛选范围；无法获取的资料保留为待核查项。

## 本地导出示例

在项目根目录运行以下命令，使用已有的 20 篇 ICML 2024 样本及判断，生成四份文档。`demo-output` 必须是新的或空的目录，重复运行时换一个目录名。

```sh
python skills/conference-paper-search/scripts/paper_pipeline.py export --papers tests/fixtures/icml2024-pmlr-sample.json --profile examples/sample-profile.json --assessments examples/sample-assessments.json --overview examples/sample-overview.json --mode recap --top-k 20 --out-dir demo-output
```

如果系统使用 `python3`，替换命令开头即可。将 `--mode recap` 改为 `--mode attend` 可导出参会模式；此命令复用已有判断，不会重新进行论文筛选。打开生成的 `demo-output/index.html` 即可浏览。

完整输入格式见[数据契约](skills/conference-paper-search/references/data-contract.md)，会议资料入口见[官方来源指南](skills/conference-paper-search/references/sources.md)。

## 目录结构

```text
skills/conference-paper-search/
  SKILL.md                    # agent 的工作流程
  agents/openai.yaml          # skill 展示信息
  references/                 # 数据契约与会议来源指南
  scripts/
    fetch_pmlr.py             # 获取 PMLR 卷及论文摘要
    paper_pipeline.py         # 分批、验证、合并与导出
    output_html.py            # 本地 HTML 页面生成
examples/                     # 兴趣、判断、导读及四文件输出示例
tests/                        # 脚本测试、真实样本及验证记录
```

## 当前状态

自动获取已实现 PMLR 已出版论文集；ICLR、NeurIPS、CVPR、ECCV、ICCV、ACL、AAAI 提供官方来源指南，可结合 agent 的网页工具或用户 CSV/JSON 导入。录用公告阶段的自动获取尚未跑通。

已有验证记录：原有 32 项脚本测试通过；按“Transformer/LLM 高效推理”方向检查 ICML 2024 官方顺序前 20 篇论文，识别 4 篇相关论文，推荐引用通过原文核验。四文件导出已检查数据一致性和脚本语法；HTML 交互尚待实际浏览器验证。样本试跑尚未评估完整会议的推荐召回率，详见[验证记录](tests/verification.md)。

运行脚本测试：

```sh
python -m unittest discover -s tests -v
```

后续逐步完善采集缓存与续跑、兴趣和资料版本绑定、会议来源适配，以及相关性等级和推荐优先级的判定标准。
