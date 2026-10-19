# Contributing to Graduate Admissions Agent Benchmark

感谢你对保研 Agent Benchmark 的关注。Issue 和 Pull Request 均欢迎；小而聚焦、附带可复现依据的改动最容易评审。

## 开始之前

- 先搜索已有的 Issue 和 Pull Request，避免重复工作。
- Bug 报告请说明运行的命令、Python 与操作系统版本、最小复现步骤，以及不含凭据的报错输出。
- 大型题库调整、评分口径变更或新的评测结果，请先开 Issue 说明动机、影响范围和验证方案，再开始实现。

## 提交范围

| 类型 | 请包含 | 不要包含 |
| --- | --- | --- |
| 代码与文档 | 聚焦的改动、相应测试或复现步骤 | API key、登录文件、个人配置、生成运行目录 |
| 题目与 rubric | 题目/案例标识、来源与必要的 schema/manifest 更新 | 私有题库、未获授权的材料、供被测 Agent 读取的评分资料 |
| 实验或结果 | 固定输入版本、内容哈希、Agent 配置和运行限制 | 编造的分数、未验证的模型身份，或把 `official=false` 的结果表述为正式认证 |

原始公开题目、评分标准及相关数据材料适用 CC BY 4.0；代码和软件文档适用 MIT。提交数据时请保留要求的署名、来源和变更说明。详见 [LICENSE-DATA](LICENSE-DATA) 与 [LICENSE](LICENSE)。

## 提交 Pull Request

1. 从最新 `main` 创建一个主题明确的分支。
2. 保持单个 PR 只解决一个问题；如改动影响题目或结果，请在描述中列出受影响的任务或记录。
3. 运行与改动相关的测试。例如：

   ```sh
   python3 -m unittest discover -s tests -v
   ```

   原生执行相关测试需要 macOS Seatbelt；如果本机无法运行，请在 PR 中说明未运行的测试和原因。
4. 在 PR 描述中写清楚：目的、主要改动、验证命令及结果，以及任何仍未解决的限制。

## 评测完整性与隐私

评分材料必须与被测 Agent 隔离。不要提交凭据、个人申请信息、私有测试集、未脱敏日志或其他不应公开的数据。发现可能泄露的敏感信息时，请不要公开提交；改用私下联系维护者的方式报告。

## Language

中文提交和 Issue 均可接受。If you prefer English, please include the same reproduction, provenance, and validation details described above.
