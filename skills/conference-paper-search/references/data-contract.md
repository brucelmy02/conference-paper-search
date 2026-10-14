# 数据契约

所有 JSON 使用 UTF-8。未知值使用 `null` 或空数组，保留未知而不补写事实。用户只需提供主题或论文；以下结构由执行 skill 的 agent 整理。

## 研究兴趣 profile.json

```json
{
  "owner": "personal",
  "topics": [
    {
      "id": "t1",
      "problem": "降低 Transformer 模型的推理计算和内存成本",
      "focus": ["量化", "注意力计算", "推理系统"],
      "constraints": [],
      "exclude": ["仅优化训练过程而不讨论推理"],
      "relation_scope": ["direct", "method_transfer", "adjacent"],
      "priority": "primary",
      "provenance": [
        {"kind": "user", "reference": "本次用户明确描述"}
      ]
    }
  ],
  "representative_papers": [],
  "notes": "这是可修改的兴趣描述。"
}
```

`owner` 为 `personal` 或 `lab`。主题 ID 唯一，`problem` 为非空字符串。`focus`、`constraints`、`exclude` 为字符串数组，不明确时为空。排除项仅来自用户或已展示的合理解释，不能因为主题材料缺失而自行添加。

`relation_scope` 表示可接受的直接关联、方法迁移、邻近方向，未指定时直接关联优先并少量探索。`priority` 为 `primary` 或 `secondary`，不使用未校准的百分比。

`provenance` 记录 `user` 或 `publication_inference`；`reference` 定位用户描述、作者主页、具体论文和年份。推断字段可以在 notes 中逐项说明。代表论文记录 `title`、`url`、`reason`，reason 未知可为 null。

## 当次任务设置

与 profile 分开保存：`conference`、`year`、`track`、`mode`（attend / recap）、`top_k`、范围说明。conference/year 应从用户或已核实的官方页面确定。默认主会，其他 track 按用户要求选择。

## 论文列表 papers.json

```json
{
  "conference": "ICML",
  "year": 2024,
  "track": "main",
  "source_url": "https://proceedings.mlr.press/v235/",
  "retrieved_at": "2026-10-14T00:00:00Z",
  "scope_note": "PMLR 235 卷中的前 20 条，用于抽样测试，未覆盖整场会议。",
  "papers": [
    {
      "id": "stable-source-id",
      "title": "实际论文标题",
      "authors": ["实际作者名"],
      "abstract": null,
      "url": "https://example.org/paper",
      "pdf_url": null,
      "acceptance": "unknown",
      "sources": [],
      "presentation": null
    }
  ]
}
```

上述 example.org 仅说明字段形状，实际记录必须引用真实来源。`id` 是稳定字符串，`title` 非空。来源未知的导入保留 `acceptance=unknown`；已核实正式录用为 `accepted`，另有 `rejected` / `withdrawn`。条件录用使用 `unknown`，另存 `source_acceptance="conditional"` 保留原始状态。论文有公开页面或出现在投稿列表，并不证明录用。

prepare 支持 envelope、原始 JSON 数组和 CSV；原始数组/CSV 无明确来源时保留未知会议、未知录用与不完整范围。CSV 至少包含 title，可选 id、authors、abstract、url、acceptance；具体分隔符见脚本帮助。作者列表尽量用 JSON 数组或约定的分隔形式。

按 ID 或相同规范化 URL 去重，同标题但不同来源的论文不直接合并。冲突信息保留或报错，不能悄悄丢弃不同录用状态。prepare 为标题与非空摘要生成 source：

```json
{
  "id": "abstract",
  "kind": "abstract",
  "text": "实际取得的摘要原文",
  "url": "https://official-source/paper",
  "locator": "Abstract"
}
```

`sources` 为当前已读取资料的证据集合。kind 为 title、abstract、full_text；正文来源另起唯一 ID，并注明章节、页码或段落。引用资料截取时标明范围；不能将未读取正文放进 source。

`presentation` 只有经过核实时使用：

```json
{
  "confirmed": true,
  "source_url": "https://official-conference/schedule",
  "time": "会议公布的时间",
  "timezone": "会议当地时区",
  "session": "官方 session",
  "location": "官方地点"
}
```

未知字段留空。source_url 与 confirmed 是显示日程的条件；有 paper 作者信息不等于该作者现场到场。

## 每篇判断 assessments.json

```json
{
  "assessments": [
    {
      "paper_id": "stable-source-id",
      "decision": "pending",
      "relevance": "unknown",
      "relation": null,
      "topic_ids": [],
      "reason": "录用状态未知，尚未取得摘要。",
      "reading_focus": "获取摘要后检查实际研究问题。",
      "differences": [],
      "evidence": [],
      "uncertainties": ["是否录用", "研究问题和方法"],
      "evidence_status": "missing",
      "priority": 3
    }
  ]
}
```

decision 为 include / exclude / pending；relevance 为 high / medium / low / unknown，和 evidence_status 分开。evidence_status 为 sufficient / limited / missing。相关性很高但录用未知仍为 pending；材料缺失不直接转为 exclude。

include 需要 confirmed accepted、已知 topic_ids、每个列出的匹配 topic 都允许的 relation、非空 reason 与 reading_focus，以及至少一条有效证据。topic_ids 只列当前关联类型成立的方向，避免某个方向允许邻近探索时让其他明确排除邻近探索的方向也收到这篇论文。exclude 也需证据与非空理由；资料缺失时优先 pending。priority 为 1（优先）、2（补充）、3（探索），只用于当前输出排序；不表示论文质量。

证据引用：

```json
{"source_id": "abstract", "quote": "该 source 中实际存在的原文片段"}
```

验证器允许空白规范化，但不允许改写 quote。模型改写或解释写在 reason / differences 中。quote 应支持匹配点；仅在文本中存在不证明语义判断正确，仍需阅读检查。资料无 URL 时不能伪造 URL，可定位本地文件并在范围说明中标明。

同一论文最多一个最终判断，合并时拒绝重复 ID。每批判断可以独立验证；缺少判断的论文计为未处理，绝不能计为不相关。

## 会后综合与整次覆盖

报告脚本生成逐篇证据与主题分组，不生成跨论文事实或趋势。agent 可以追加有来源的比较，注明哪些论文支持该句，以及证据来自摘要还是正文。

整次统计至少包含：来源与日期、scope_note、论文总数、已评估数、推荐数、排除数、pending 数、未评估数、摘要缺失数、未知录用数。多卷或多 track 合并需要记录各自来源；一个卷完整处理不代表整个会议完整覆盖。

## 四文件输出契约

同一次 `export` 先验证论文、兴趣、判断和可选导读，再从同一组记录生成以下四个文件。输出目录需为新的空目录；更新兴趣、判断或导读后重新统一导出，避免不同格式中的推荐理由、证据或状态出现分歧。四文件的展示范围可以不同，论文身份和事实字段必须一致。

| 文件 | 展示范围与用途 |
|---|---|
| `report.md` | 导读、覆盖说明、阅读导航和逐篇详情。参会模式优先展示 top-k 精选；会后模式按方向展示全部已确认相关论文，并列精选代表作。待核查项注明状态。 |
| `papers.csv` | 全部 `include` 和 `pending` 记录，提供可排序、可筛选的完整相关目录；top-k 不截断 CSV。使用 UTF-8 BOM 便于 Excel 读取。 |
| `results.json` | 保留全部论文、原始来源、兴趣、覆盖情况、导读和判断，包括 `exclude` 与未处理记录，供核查和后续问答使用。 |
| `index.html` | 内嵌完整数据、样式和脚本的单文件；无需服务器或联网加载即可搜索、筛选、排序和展开详情。默认聚焦相关论文；排除与未处理记录通过主动状态筛选查看。 |

### 导读 overview.json

导读可选，由执行 skill 的 agent 根据已读资料写入，脚本负责验证引用和展示，不生成研究结论。结构如下：

```json
{
  "lead": "简短导读，说明本次筛选结果及建议的阅读起点。",
  "themes": [
    {
      "topic_id": "t1",
      "text": "有论文依据的子方向总结或比较。",
      "paper_ids": ["stable-source-id"]
    }
  ],
  "attendance_questions": [
    {
      "paper_id": "stable-source-id",
      "questions": ["由已读取内容产生的具体交流问题。"]
    }
  ]
}
```

`lead` 为字符串，`themes` 和 `attendance_questions` 为数组；无相应内容时可以为空。`topic_id` 必须存在于 profile，`paper_id` 和 `paper_ids` 必须引用本次已纳入的论文，未知或未纳入的引用应修正后再导出。主题中的 `paper_ids` 是读者核查该段总结的入口，不替代逐篇证据。描述跨论文比较时，核对这些论文的摘要或正文确实支持 text。交流问题可以提出尚未解决的疑问，不能把未经核实的实验结果写成问题前提。没有 overview 时只展示已记录的筛选结果和覆盖说明，不生成占位总结。

### 身份、状态与记录

每篇保留原始稳定 `id`；所有格式使用同一个 `display_id`。展示 ID 由稳定 ID 的哈希生成，不依赖当前排名、批次位置或 top-k，便于用户直接说“展开这篇”或“比较这两篇”。排序或筛选不得重新编号；判断中的 `paper_id` 继续指向原始稳定 ID。

JSON bundle 包含 `metadata`、`coverage`、`profile`、`overview` 和 `papers`。`metadata` 保存会议、年份、track、来源、获取日期、范围及输出模式等任务信息；`coverage` 使用本契约的整次统计。每条 papers 记录保留原始 paper，关联 `assessment`（未处理时为 `null`）、`display_id` 和从 profile 解析的 `topic_labels`。原始来源与证据文本必须保留，不能只输出模型概述。未处理与已判为无关是不同状态。

CSV 将相关与待核查记录展开为便于表格筛选的列，包含稳定 ID、展示 ID、标题、作者、方向、判断状态、关联类型、相关性、阅读优先级、推荐理由、阅读重点、证据状态和论文链接。已核实的展示信息可以提供；未知日程留空。多作者、多方向和多条证据的单元格保留边界，导出时正确转义逗号、引号和换行。完整原文和全部证据由 JSON 与 HTML 提供，CSV 无须堆积整段摘要。

### HTML 阅读与查询

搜索覆盖标题、作者、方向、两种 ID、推荐理由、阅读建议、摘要和已核实的展示字段；筛选覆盖研究方向、关联类型、阅读优先级、记录状态及个人阅读标记，并提供排序和详情展开。Markdown 中的展示 ID 直接链接到 HTML 的对应详情。展开后可查看推荐理由、匹配方向、阅读重点、关键差异、原文证据、来源链接和待核查事项。搜索或筛选无结果时明确提示，不能据此更改覆盖统计。

参会模式默认显示 top-k 精选，并提供切换到全部相关论文的入口；会后模式默认显示全部已确认相关论文。待核查、排除和未处理状态可以主动选择查看。场次、时间与地点沿用论文记录中的核实条件，不根据作者或录用标签补造现场信息。

用户可将论文标为未读、待读、已读或重点关注。这些个人阅读标记只保存在当前浏览器，并可手动导出；它们不会自动同步至 Markdown、CSV 或 JSON，也不改变研究相关性判断。页面应说明保存范围和导出入口，不能将阅读状态混同为评估状态。
