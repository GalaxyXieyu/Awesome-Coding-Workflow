# Claude Code Skills 学习指南

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blue)](https://claude.ai/code)

> 系统学习 Claude Code Skills 的编写、设计与最佳实践

## 项目目标

帮助开发者快速理解和掌握 Claude Code Skills 的：
- **核心概念** - Skills 与 Rules 的区别和联动
- **编写方法** - 从零开始编写高质量 Skills
- **抽象模型** - 理解 Skills 的设计模式
- **评估指标** - 量化 Skills 的效果
- **最佳实践** - 快速挖掘和复用 Skills

## 快速开始

### 安装

```bash
git clone https://github.com/YOUR_USERNAME/Awesome-Coding-Workflow.git
cd Awesome-Coding-Workflow
make install
```

### 目录结构

```
.
├── docs/                          # 学习文档
│   ├── 01-skills-basics.md        # Skills 基础概念
│   ├── 02-skills-components.md    # Skills 组成部分
│   ├── 03-skills-integration.md   # Skills 联动机制
│   ├── 04-skills-model.md         # Skills 抽象模型
│   ├── 05-skills-import.md        # 导入引用方法
│   ├── 06-skills-evaluation.md    # 效果评估指标
│   └── 07-skills-sop.md           # 挖掘 Skills 的 SOP
├── examples/                      # 示例 Skills
│   └── data-exploration/          # 数据探索 Skills
├── templates/                     # Skills 模板
│   ├── basic-skill.md             # 基础模板
│   └── advanced-skill.md          # 高级模板
├── scripts/                       # 工具脚本
│   └── install.sh                 # 安装脚本
└── README.md
```

## 学习路线图

### 第一阶段：理解基础

| 主题 | 文档 | 预计时间 |
|------|------|----------|
| 为什么需要 Skills 和 Rules | [01-skills-basics.md](docs/01-skills-basics.md) | 30min |
| Skills 组成部分 | [02-skills-components.md](docs/02-skills-components.md) | 30min |
| 各部分如何联动 | [03-skills-integration.md](docs/03-skills-integration.md) | 30min |

### 第二阶段：深入理解

| 主题 | 文档 | 预计时间 |
|------|------|----------|
| Skills 抽象模型 | [04-skills-model.md](docs/04-skills-model.md) | 1h |
| 导入引用方法 | [05-skills-import.md](docs/05-skills-import.md) | 30min |
| 效果评估指标 | [06-skills-evaluation.md](docs/06-skills-evaluation.md) | 1h |

### 第三阶段：实战应用

| 主题 | 文档 | 预计时间 |
|------|------|----------|
| 挖掘 Skills 的 SOP | [07-skills-sop.md](docs/07-skills-sop.md) | 1h |
| 数据探索 Skills 实战 | [examples/data-exploration](examples/data-exploration/) | 1h |

## 核心概念

### Skills vs Rules

| 对比项 | Skills | Rules |
|--------|--------|-------|
| 作用域 | 特定任务/场景 | 全局行为约束 |
| 触发方式 | 按需激活 | 始终生效 |
| 复杂度 | 可包含复杂流程 | 通常是简单规则 |
| 复用性 | 跨项目复用 | 项目内生效 |

### Skills 组成要素

```
Skills
├── 触发条件 (Trigger)      # 何时激活
├── 上下文 (Context)        # 需要什么信息
├── 执行逻辑 (Logic)        # 做什么
├── 输出规范 (Output)       # 输出什么格式
└── 约束条件 (Constraints)  # 边界和限制
```

## 贡献指南

欢迎提交 PR 来：
- 补充学习文档
- 分享你的 Skills 实践
- 改进示例代码
- 修复文档错误

## 相关资源

- [Claude Code 官方文档](https://docs.claude.com)
- [myclaude - 多智能体工作流](https://github.com/cexll/myclaude)

## 许可证

MIT License - 查看 [LICENSE](LICENSE)
