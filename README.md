# Awesome Coding Workflow

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blue)](https://claude.ai/code)

> Claude Code Skills 集合 - 可直接在 Claude Code 中作为 Plugin Marketplace 使用

## 快速使用

### Claude Code 中安装

```bash
# 1. 添加为 Plugin Marketplace
/plugin marketplace add GalaxyXieyu/Awesome-Coding-Workflow

# 2. 浏览并安装 Skills
# 选择 Browse and install plugins -> awesome-coding-workflow -> 选择需要的 skill

# 或者直接安装特定 skill
/plugin install data-explorer@awesome-coding-workflow
/plugin install langgraph-agent@awesome-coding-workflow
```

### Claude.ai 网页端

1. 进入 **Settings > Capabilities**
2. 确保 **Code execution and file creation** 已启用
3. 点击 **Upload skill** 上传 skill 的 ZIP 文件

## 目录结构

```
.
├── skills/                        # Skills 集合
│   ├── agent-architector/         # Agent 架构设计专家
│   ├── data-explorer/             # 数据探索专家
│   └── langgraph-agent/           # LangGraph Agent 开发专家
├── template/                      # Skill 模板
│   ├── basic-skill.md             # 基础模板
│   └── advanced-skill.md          # 高级模板
├── spec/                          # Skill 编写规范
│   └── 00-skill-writing-guide.md  # 编写指南
├── docs/                          # 学习文档
│   ├── 01-skills-basics.md        # Skills 基础概念
│   ├── 02-skills-components.md    # Skills 组成部分
│   ├── 03-skills-integration.md   # Skills 联动机制
│   ├── 04-skills-model.md         # Skills 抽象模型
│   ├── 05-skills-import.md        # 导入引用方法
│   ├── 06-skills-evaluation.md    # 效果评估指标
│   └── 07-skills-sop.md           # 挖掘 Skills 的 SOP
└── README.md
```

## Skills 列表

| Skill | 描述 | 适用场景 |
|-------|------|----------|
| [data-explorer](skills/data-explorer/) | 数据层探索专家 | 查询数据、理解结构、优化性能、复用现有方法 |
| [langgraph-agent](skills/langgraph-agent/) | LangGraph Agent 开发专家 | 基于 LangGraph 构建生产级 Agent |
| [agent-architector](skills/agent-architector/) | Agent 架构设计专家 | 设计和实现 AutoAgents/LangGraph Agent |

## 创建自定义 Skill

### Skill 基本结构

```
my-skill/
├── SKILL.md          # 必须：核心指令文件
├── references/       # 可选：参考资料
└── scripts/          # 可选：可执行脚本
```

### SKILL.md 格式

```yaml
---
name: my-skill-name          # 必填，64字符内
description: 描述技能用途    # 必填，200字符内
---

# Skill 名称

[Claude 执行时遵循的指令]
```

参考 [template/](template/) 目录获取完整模板。

## 学习资源

| 主题 | 文档 |
|------|------|
| Skills 基础概念 | [01-skills-basics.md](docs/01-skills-basics.md) |
| Skills 组成部分 | [02-skills-components.md](docs/02-skills-components.md) |
| Skills 联动机制 | [03-skills-integration.md](docs/03-skills-integration.md) |
| Skills 抽象模型 | [04-skills-model.md](docs/04-skills-model.md) |
| 导入引用方法 | [05-skills-import.md](docs/05-skills-import.md) |
| 效果评估指标 | [06-skills-evaluation.md](docs/06-skills-evaluation.md) |
| 挖掘 Skills 的 SOP | [07-skills-sop.md](docs/07-skills-sop.md) |

## 相关资源

- [Anthropic Skills 官方仓库](https://github.com/anthropics/skills)
- [Claude Code 官方文档](https://docs.claude.com)

## 许可证

MIT License - 查看 [LICENSE](LICENSE)
