# 保研 Agent Benchmark

本项目是屿智同行的保研 Agent 评测项目，评测 Agent 配置（执行系统与模型组合）在保研择校、申请规划与建议更新中的表现。当前结果覆盖 8 组 Agent 配置。

题库包含70道中文任务、23组案例和83个作答阶段，配套逐题评分标准与参考项目。公开数据无需申请访问；评分资料虽可下载，但评测时不得提供给被测 Agent。

[English](README.md) · [评测结果](#评测结果) · [快速开始](#快速开始) · [题目与评分](data/questions-and-scoring.md) · [Hugging Face 数据集](https://huggingface.co/datasets/yuxin7778/baoyan-agent-benchmark) · [评测方法](docs/result-methodology.md)

## 评测结果

本榜单基于70道公开题的评测记录汇总，展示 8 组 Agent 配置的平均得分与完成率。评测设置和评分说明见[文档](docs/result-methodology.md)。

| 排名 | Agent 配置（系统 + 模型） | 题数 | 完成率 | 均分 / 100 |
| ---: | --- | ---: | ---: | ---: |
| 1 | [Codex + GPT Sol 6.1](experiments/records70/models/gpt-6-1-sol/README.md) | 70 | 70/70 (100.0%) | 79.08 |
| 2 | [Codex + GPT Astra 6](experiments/records70/models/gpt-6-astra/README.md) | 70 | 70/70 (100.0%) | 78.36 |
| 3 | [DSH + DeepSeek V4.1 Flash](experiments/records70/models/deepseek-v4-1-flash/README.md) | 70 | 70/70 (100.0%) | 68.16 |
| 4 | [Volcengine Managed Agent + GLM 5.3 Flash](experiments/records70/models/ark-glm-5-3-flash-260828/README.md) | 70 | 70/70 (100.0%) | 66.80 |
| 5 | [Qwen Code + Qwen 3.8 Max](experiments/records70/models/qwen3-8-max-0902/README.md) | 70 | 70/70 (100.0%) | 64.24 |
| 6 | [Kimi Code + Kimi K3](experiments/records70/models/kimi-k3/README.md) | 70 | 70/70 (100.0%) | 58.96 |
| 7 | [Antigravity + Gemini 3.8 Flash](experiments/records70/models/antigravity-gemini-3-8-flash-high/README.md) | 70 | 70/70 (100.0%) | 58.23 |
| 8 | [Antigravity + Gemini 3.1 Pro](experiments/records70/models/antigravity-gemini-3-1-pro-high/README.md) | 70 | 70/70 (100.0%) | 55.55 |

8 组 Agent 配置各完成 70 题；当前共 0 题超时。结果来自不同真实运行，输入版本与预算并非全部一致，公开记录也并非全部包含完整工具轨迹；不能据榜单推断统一运行条件。

当前70题及评分标准均已由维护者确认完成教师校准。难度标签经负责人确认：简单14题（20%）、中等34题（48.57%）、困难22题（31.43%）；不代表独立双标复核。逐题评分记录仍保留生成时的 `scored_draft` 与 `teacher_calibration` 标签；`official=false` 是独立的结果认证标记。

### 不同 Agent 配置在保研任务上的表现

![不同 Agent 配置在保研任务上的表现](docs/figures/dev70-current/fig1_zh_2l.png)

8 组 Agent 配置在 70 项评测任务上的平均得分（满分 100 分）。

![70题难度分布](docs/figures/dev70-current/fig_diff_zh.png?v=5dd8d556e42a)

[评分数据](experiments/records70/score-summary-70.json) · [逐题得分](experiments/records70/score-details-70.json) · [按 Agent 配置查阅答卷与评分](experiments/records70/README.md)

## 快速开始

在仓库根目录执行。原生自动运行需要macOS Seatbelt、Python 3.10+（Kimi订阅配置需要3.11+）；框架只用标准库，无需`pip install`。先安装相应官方客户端，并准备自己的订阅登录或API Key。

按当前[Agent注册表](config/agents-cli.example.json)选择配置；表内ID用于`--agent`，不是客户端模型参数：

| Agent 配置 | Agent ID | 客户端 | 模板认证 |
| --- | --- | --- | --- |
| Codex + GPT Astra 6 | `gpt-6-astra` | Codex / `codex` | ChatGPT订阅 |
| Codex + GPT Sol 6.1 | `gpt-6-1-sol` | Codex / `codex` | ChatGPT订阅 |
| Claude Opus | `claude-opus-5-5` | Claude Code / `claude` | 订阅OAuth |
| Claude Sonnet | `claude-sonnet-5-5` | Claude Code / `claude` | 订阅OAuth |
| Gemini Flash | `antigravity-gemini-3-8-flash-high` | Antigravity / `agy` | 订阅 |
| DeepSeek Flash | `deepseek-v4-1-flash` | DeepSeek Harness / `dsh` | API |
| Qwen Max | `qwen3-8-max-0902` | Qwen Code / `qwen` | DashScope API |
| Kimi K3 | `kimi-k3` | Kimi Code / `kimi` | 订阅OAuth |

所有配置共用以下流程。将`AGENT`换成上表ID，运行时沿用所选认证方式：

```sh
AGENT=gpt-6-1-sol
python3 -m benchmark setup --agent "$AGENT"
python3 -m benchmark cli-check --agent "$AGENT"
python3 -m benchmark cli-batch \
  --selection config/selections/current.json \
  --agent "$AGENT" --out "./runs/current-$AGENT"
```

`setup`保存本机配置；`cli-check`返回`ready_for_trial`后先试跑一道题。批跑默认只预览70题、83阶段，不调用模型；添加`--execute`才使用所选账号额度。多模型时，对每项完成配置和检查，再在批跑命令中重复`--agent`，例如`--agent gpt-6-1-sol --agent claude-opus-5-5`，并使用新输出目录。

评分可用独立Codex订阅会话审阅导出的材料；可选API自动评审需另行配置。单题试跑、订阅评审、API评审与报告步骤见[快速开始](docs/quick-start.md)，安装、认证和多阶段细节见[原生CLI指南](docs/native-cli.md)。

## 数据与评分

- **21道择校推荐题**：比较推荐项目与学生条件的匹配度。
- **36道规划与决策题**：评估准备路径、风险判断和可执行建议。
- **13道两阶段题**：在同一会话补充信息，观察Agent是否更新建议；两阶段合为一道题评分。

![70题分布](docs/figures/dev70-current/fig_task_zh.png?v=730083e9fb8c)

每题100分。完整择校题的参考项目匹配占70分、推荐质量占30分；独立评审读取完整答卷，评分材料与答题进程隔离。

![同一会话两阶段评测流程](docs/figures/dev70-current/fig2_zh.png)

两阶段任务依次提供初始情境 S₀ 与新增信息 S₁，在同一会话中获得初始回复 A₀ 与修订回复 A₁，并联合评分。图中的一月到三月、转向直博情境对应公开任务 [O03-04](data/staged-dev/O03-04/task.json)；E1–E5 对应本例的五项评分标准，权重依次为 25、25、25、15、10 分，详见 [O03-04 评分标准](data/staged-dev/O03-04/rubric.json)。图中 (b) 是任务要求示意，(c) 是评分标准。

[全部题目与评分条件](data/questions-and-scoring.md) · [题库索引](config/selections/current.json) · [数据结构](docs/dataset.md) · [评分通则](docs/scoring.md)


### 分题型表现

![8 组 Agent 配置在三类任务上的表现](docs/figures/dev70-current/fig3_zh_2l.png)

择校推荐 21 题、规划与决策 36 题、两阶段任务 13 题；图示为各类任务的平均得分（满分 100 分），各类最高分以粗体标出。

逐题状态、计分区间和完整答卷见[逐题结果](experiments/records70/score-details-70.json)与[按 Agent 配置查阅答卷与评分](experiments/records70/README.md)。

## 方法与复现

[评测口径与运行记录](docs/result-methodology.md)说明本次结果的组成与限制；[评审流程](docs/review-protocol.md)说明如何独立评分。[复现指南](docs/reproduction.md)涵盖冻结输入、交卷与成绩复核，数据导出见[本地导出说明](docs/publication.md)。

## 关于项目

本项目是**屿智同行**的保研 Agent 评测项目。

### 团队

**Yonghao Zhang**为CEO、清华大学计算机科学硕士；**Yichen Wang**为CTO及Sprix AI项目负责人。

## 参与贡献与引用

欢迎通过 Issue 或 Pull Request 改进题目、评分标准、评测工具和文档。贡献流程、评测完整性边界和验证要求见 [CONTRIBUTING.md](CONTRIBUTING.md)。引用代码或工具请用 [MIT 软件引用](CITATION.cff)；引用题目或评分资料请用 [CC BY 4.0 数据集引用](https://huggingface.co/datasets/yuxin7778/baoyan-agent-benchmark/blob/main/CITATION.cff)。注明版本、内容哈希及 Agent 配置。

## 致谢

感谢保研岛为本评测提供数据支持。

## 许可

代码及软件文档采用 [MIT](LICENSE) 许可；原创公开题目、评分标准等数据材料采用 [CC BY 4.0](LICENSE-DATA) 许可，具体范围以许可文件为准。第三方资料保留各自权利。
