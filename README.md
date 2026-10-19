# Graduate Admissions Agent Benchmark

This is 屿智同行's benchmark project for graduate admissions agents, evaluating agent configurations (execution systems paired with models) for admissions advising, application planning and updating advice as student information changes. The current results cover eight agent configurations.

The benchmark contains 70 Chinese-language tasks, 23 cases and 83 answer stages, with per-task rubrics and reference programs. The public dataset is available without access approval; scoring materials must be withheld from the agents being evaluated.

[简体中文](README.zh-CN.md) · [Results](#evaluation-results) · [Quick start](#quick-start) · [Questions and scoring](data/questions-and-scoring.md) · [Hugging Face dataset](https://huggingface.co/datasets/yuxin7778/baoyan-agent-benchmark) · [Methodology](docs/result-methodology.md)

## Evaluation results

This leaderboard summarizes evaluation records for 70 public tasks, showing the mean score and completion rate of eight agent configurations. See the [documentation](docs/result-methodology.md) for evaluation settings and scoring.

| Rank | Agent configuration (system + model) | Tasks | Completion | Mean score / 100 |
| ---: | --- | ---: | ---: | ---: |
| 1 | [Codex + GPT Sol 6.1](experiments/records70/models/gpt-6-1-sol/README.md) | 70 | 70/70 (100.0%) | 79.08 |
| 2 | [Codex + GPT Astra 6](experiments/records70/models/gpt-6-astra/README.md) | 70 | 70/70 (100.0%) | 78.36 |
| 3 | [DSH + DeepSeek V4.1 Flash](experiments/records70/models/deepseek-v4-1-flash/README.md) | 70 | 70/70 (100.0%) | 68.16 |
| 4 | [Volcengine Managed Agent + GLM 5.3 Flash](experiments/records70/models/ark-glm-5-3-flash-260828/README.md) | 70 | 70/70 (100.0%) | 66.80 |
| 5 | [Qwen Code + Qwen 3.8 Max](experiments/records70/models/qwen3-8-max-0902/README.md) | 70 | 70/70 (100.0%) | 64.24 |
| 6 | [Kimi Code + Kimi K3](experiments/records70/models/kimi-k3/README.md) | 70 | 70/70 (100.0%) | 58.96 |
| 7 | [Antigravity + Gemini 3.8 Flash](experiments/records70/models/antigravity-gemini-3-8-flash-high/README.md) | 70 | 70/70 (100.0%) | 58.23 |
| 8 | [Antigravity + Gemini 3.1 Pro](experiments/records70/models/antigravity-gemini-3-1-pro-high/README.md) | 70 | 70/70 (100.0%) | 55.55 |

All eight agent configurations completed 70 tasks; 0 current tasks timed out. These results combine different real runs with input versions and budgets that are not fully uniform. Complete tool traces are not available for every public record; the leaderboard does not imply uniform execution conditions.

All 70 current tasks and rubrics have owner-confirmed teacher calibration. The owner-approved difficulty labels are 14 easy (20%), 34 medium (48.57%) and 22 hard (31.43%); this is not an independent double review. Per-answer `scored_draft` and `teacher_calibration` labels remain in the captured scoring records. `official=false` is a separate result-certification flag.

### Performance of agent configurations on graduate admissions tasks

![Performance of agent configurations on graduate admissions tasks](docs/figures/dev70-current/fig1_en_2l.png)

Mean scores of eight agent configurations across 70 evaluation tasks (maximum = 100).

![70-task difficulty distribution](docs/figures/dev70-current/fig_diff_en.png?v=53545e440b48)

[Score data](experiments/records70/score-summary-70.json) · [Per-task results](experiments/records70/score-details-70.json) · [Answers and scores by agent configuration](experiments/records70/README.md)

## Quick start

Run from the repository root. Automated native execution requires macOS Seatbelt and Python 3.10+ (3.11+ for Kimi subscription configuration). The framework uses only the standard library; no `pip install` is needed. Install the official client and prepare your own subscription login or API key.

Choose a configuration from the current [agent registry](config/agents-cli.example.json). These IDs are used with `--agent`; they are not client model arguments:

| Agent configuration | Agent ID | Client | Template authentication |
| --- | --- | --- | --- |
| Codex + GPT Astra 6 | `gpt-6-astra` | Codex / `codex` | ChatGPT subscription |
| Codex + GPT Sol 6.1 | `gpt-6-1-sol` | Codex / `codex` | ChatGPT subscription |
| Claude Opus | `claude-opus-5-5` | Claude Code / `claude` | Subscription OAuth |
| Claude Sonnet | `claude-sonnet-5-5` | Claude Code / `claude` | Subscription OAuth |
| Gemini Flash | `antigravity-gemini-3-8-flash-high` | Antigravity / `agy` | Subscription |
| DeepSeek Flash | `deepseek-v4-1-flash` | DeepSeek Harness / `dsh` | API |
| Qwen Max | `qwen3-8-max-0902` | Qwen Code / `qwen` | DashScope API |
| Kimi K3 | `kimi-k3` | Kimi Code / `kimi` | Subscription OAuth |

Every configuration uses the same workflow. Replace `AGENT` with an ID above and retain its chosen authentication mode:

```sh
AGENT=gpt-6-1-sol
python3 -m benchmark setup --agent "$AGENT"
python3 -m benchmark cli-check --agent "$AGENT"
python3 -m benchmark cli-batch \
  --selection config/selections/current.json \
  --agent "$AGENT" --out "./runs/current-$AGENT"
```

`setup` saves local configuration. After `cli-check` returns `ready_for_trial`, try one task first. Batch execution defaults to a preview of 70 tasks and 83 stages without model calls; add `--execute` to use your account allowance. For multiple models, configure and check each, then repeat `--agent`, for example `--agent gpt-6-1-sol --agent claude-opus-5-5`, and use a new output directory.

Scoring can use a separate Codex subscription session to review exported materials. Optional API judging requires separate configuration. See the [quick start](docs/quick-start.en.md) for trials, subscription review, API judging and reports, and the [native CLI guide](docs/native-cli.md) for installation, authentication and multiple stages.

## Dataset and scoring

- **21 recommendation tasks:** assess how well suggested programs match the student's background and constraints.
- **36 planning and decision tasks:** evaluate preparation plans, risk assessment and actionable advice.
- **13 two-stage tasks:** release new information within the same session and test whether the agent updates its advice. Both stages receive one task score.

![70-task distribution](docs/figures/dev70-current/fig_task_en.png?v=5997bdd329f0)

Each task is worth 100 points. Full recommendation tasks allocate 70 points to reference-program matching and 30 to recommendation quality. A separate reviewer scores the full answer; rubrics stay outside the answering process.

![Two-stage evaluation within a single session](docs/figures/dev70-current/fig2_en.png)

Two-stage tasks supply initial context S₀ followed by updated information S₁ in the same session, producing initial response A₀ and revised response A₁ for joint scoring. The January-to-March scenario and shift to direct PhD applications correspond to public task [O03-04](data/staged-dev/O03-04/task.json). E1–E5 correspond to this example’s five scoring criteria, weighted 25, 25, 25, 15 and 10 points; see the [O03-04 rubric](data/staged-dev/O03-04/rubric.json). Panel (b) illustrates task requirements, and panel (c) shows the rubric.

[All questions and criteria](data/questions-and-scoring.md) · [Task index](config/selections/current.json) · [Data format](docs/dataset.md) · [Scoring rules](docs/scoring.md)


### Results by task type

![Eight agent configurations compared across three task categories](docs/figures/dev70-current/fig3_en_2l.png)

The categories contain 21 recommendation tasks, 36 planning and decision tasks, and 13 two-stage tasks. Scores are category means out of 100; the highest score in each category is bold.

See [per-task results](experiments/records70/score-details-70.json) and [public answers](experiments/records70/README.md) for statuses, score intervals and full answer text.

## Methodology and reproduction

[Evaluation and run records](docs/result-methodology.md) document the composition and limitations of these results; the [review protocol](docs/review-protocol.md) describes independent scoring. The [reproduction guide](docs/reproduction.md) covers frozen inputs, submissions and score verification. See [local export](docs/publication.md) for dataset export.

## About the project

This is **屿智同行**'s benchmark project for graduate admissions agents.

### Team

**Yonghao Zhang** is CEO and holds a master's degree in Computer Science from Tsinghua University; **Yichen Wang** is CTO and project lead.

## Contributing and citation

Contributions to questions, rubrics, evaluation tools and documentation are welcome through Issues and Pull Requests. See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow, evaluation-integrity boundaries and validation expectations. Cite the [MIT-licensed software](CITATION.cff) for code and tooling, and the [CC BY 4.0 dataset](https://huggingface.co/datasets/yuxin7778/baoyan-agent-benchmark/blob/main/CITATION.cff) for tasks or rubrics. Record the version, content hashes and agent configuration used.

## Acknowledgements

We thank 保研岛 for providing data for this benchmark.

## License

Code and software documentation are licensed under [MIT](LICENSE). Original public task definitions, rubrics and related dataset materials are licensed under [CC BY 4.0](LICENSE-DATA), within the scope specified in the license file. Third-party materials retain their respective rights.
