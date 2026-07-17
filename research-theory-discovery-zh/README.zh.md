# 研究理论发现 Skill

一个需要显式调用的开放式科学与技术研究 skill，外加一套可选的强制执行 harness，让这套协议
不只是模型可以选择性遵守的文字。

这个目录是仓库里成对的一半：`research-theory-discovery/`（英文版）和
`research-theory-discovery-zh/`（本目录，中文版）。两者共用上一级的 `../harness/` 目录——
harness 是语言无关的代码和 hook，不是需要按语言翻译的文字，所以不为每种语言各存一份。
如果你只单独克隆了这个文件夹，记得把 `../harness/` 也拿上；`SKILL.zh.md` 的"需要时读取"
一节里用相对路径链接到它，默认它是同级目录。

## 安装（仅 skill，prompt 层）

Codex：

把这个文件夹复制到以下位置之一：

- 仓库作用域：`.agents/skills/research-theory-discovery/`
- 用户作用域：`~/.agents/skills/research-theory-discovery/`

如果没有出现，重启 Codex。

Claude Code：

把这个文件夹和 `../harness/` 作为同级目录一起复制到 `~/.claude/skills/`（个人级，所有项目生效）
或 `<project>/.claude/skills/`（项目级）：

```text
~/.claude/skills/research-theory-discovery/   <- 这个文件夹
~/.claude/skills/harness/                     <- ../harness/，这样 SKILL.md 里 ../harness/... 的链接才能解析
```

`harness/` 自己没有 `SKILL.md`，所以 Claude Code 不会把它当成单独的 skill——把它一起复制过去，
只是为了让安装后 `SKILL.md` 里的相对引用能正常解析。之后重启会话。

## 调用

```text
Use the $research-theory-discovery skill to analyze this research problem: ...
```

或者通过 `/skills` 选择。该 skill 故意关闭隐式调用——Claude Code 端是 `SKILL.md` frontmatter 里的
`disable-model-invocation: true`，Codex 端是 `agents/openai.yaml` 里的
`policy.allow_implicit_invocation: false`——避免干扰常规编码和调试。

## 安装 harness（可选，强制执行协议而不只是描述它）

纯 skill 是 prompt 层的：没有任何机制阻止模型跳过子智能体审查，或忘记更新研究树。`../harness/`
（见 `../harness/README.md`）在目标*研究*仓库（也就是你实际做研究的仓库，和你安装 skill 的位置
是两回事）之上加了三层强制：

- **Layer C —— git hooks。** `pre-commit` 拦截暂存了无效 `research_tree.json` 的提交；
  `commit-msg` 拦截裁剪节点却没在提交信息里写 `Pruning:`/`Recovery:` 的提交。纯 stdlib Python +
  POSIX sh，对任何 agent 都生效，不限于 Claude Code。
- **Layer B —— Claude Code hooks。** `PostToolUse` hook 在 `research_tree.json` 被编辑的瞬间
  重新校验；在写结论/报告类文件但树没有对应改动时提醒。`Stop` hook 在树处于无效状态时
  （未审核的"confirmed"节点、未关闭的假胜利路径、缺失的裁剪记录）阻止结束当前回合。
- **Layer A —— 一个 `Workflow` 脚本。** `workflows/research-cycle.js` 把"假设生成 -> 必要性审查
  -> 预注册预测"（`explore` 阶段）和"审计 -> 独立审查 -> 树节点"（`confirm` 阶段）做成确定性
  多智能体控制流，子智能体审查不再是模型可以选择跳过的步骤——脚本本身会调用它。

安装到目标研究仓库：

```bash
python ../harness/scripts/install_harness.py /path/to/target/repo
```

这会把校验脚本复制到 `<repo>/.research-harness/`，安装 git hooks（如果目标位置已有同名 hook，
会链式调用而不是覆盖），并打印剩下需要手动做的事：把 `harness/hooks/settings.snippet.json`
合并进目标仓库的 `.claude/settings.json`，以及如果想让 Layer A 以 workflow 形式可用，
复制 `harness/workflows/research-cycle.js` + `harness/agents/claude/*.md` 过去。
settings.json 和 workflow/agent 注册表不会被自动改动，因为它们是用户自己的文件，
在 git hook 能触及的范围之外。

完整设计理由、每一层实际能强制什么/不能强制什么、已知局限，见 `../harness/README.md`。

## 内容（本目录）

- `SKILL.md`：核心工作流和输出契约
- `references/research-protocol.md`：扩展科学方法
- `references/output-schema.md`：可复用账本和模板
- `evals/prompts.csv`：触发和行为测试提示
- `evals/quick-check.md`：日常抽查单次回答用的 pass/fail 清单
- `evals/rubric.md`：28 分制评分 rubric，仅用于 skill 迭代会话，不是每次回答都打分
- `agents/openai.yaml`：Codex UI 元数据和显式调用策略

## 内容（`../harness/`，与英文版共用）

- `README.md`：harness 设计理由、测试过什么、已知局限
- `scripts/validate_tree.py`、`check_false_victory.py`、`detect_new_pruning.py`、
  `install_harness.py`、`render_research_tree.py`：harness 脚本（Layer C + 安装器 + 可视化）
- `hooks/pre-commit`、`hooks/commit-msg`：git hooks（Layer C）
- `hooks/claude/*.py`、`hooks/settings.snippet.json`：Claude Code hooks（Layer B）
- `workflows/research-cycle.js`：确定性多智能体研究流程（Layer A）
- `agents/claude/*.md`：Layer A workflow 使用的 Claude Code 子智能体定义
