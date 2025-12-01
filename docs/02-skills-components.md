# Skills 组成部分

## 核心组件

一个完整的 Skill 通常包含以下组成部分：

```
Skill
├── 1. 元信息 (Metadata)
├── 2. 触发条件 (Trigger)
├── 3. 上下文要求 (Context)
├── 4. 执行逻辑 (Logic)
├── 5. 输出规范 (Output)
└── 6. 约束条件 (Constraints)
```

## 1. 元信息 (Metadata)

描述 Skill 的基本信息：

```markdown
---
name: data-exploration
version: 1.0.0
description: 自动探索和分析数据集
author: your-name
tags: [data, analysis, exploration]
---
```

**关键字段**：
- `name` - 唯一标识符，用于调用
- `version` - 版本号，便于管理更新
- `description` - 简短描述用途
- `tags` - 分类标签，便于检索

## 2. 触发条件 (Trigger)

定义 Skill 何时被激活：

```markdown
## 触发条件

### 显式触发
- 用户使用命令 `/explore-data`
- 用户明确请求"分析这个数据集"

### 自动触发
- 检测到用户上传了 CSV/Excel 文件
- 用户提到"数据探索"、"数据分析"等关键词
```

**触发类型**：
- **显式触发** - 用户主动调用
- **条件触发** - 满足特定条件自动激活
- **混合触发** - 两者结合

## 3. 上下文要求 (Context)

Skill 执行所需的信息：

```markdown
## 上下文要求

### 必需信息
- 数据源（文件路径/数据库连接）
- 数据格式（CSV/JSON/SQL）

### 可选信息
- 分析目标（探索性/验证性）
- 关注字段
- 数据字典
```

## 4. 执行逻辑 (Logic)

Skill 的核心处理流程：

```markdown
## 执行步骤

### Step 1: 数据加载
- 识别数据格式
- 加载数据到内存
- 处理编码问题

### Step 2: 基础分析
- 数据维度（行数、列数）
- 字段类型推断
- 缺失值统计

### Step 3: 统计分析
- 数值型：均值、中位数、标准差、分布
- 类别型：频次、占比、基数

### Step 4: 质量评估
- 完整性检查
- 一致性检查
- 异常值检测

### Step 5: 生成报告
- 汇总发现
- 可视化建议
- 后续分析建议
```

## 5. 输出规范 (Output)

定义输出格式和内容：

```markdown
## 输出规范

### 输出格式
Markdown 报告，包含以下章节：

### 报告结构
1. **数据概览** - 维度、字段列表
2. **字段详情** - 每个字段的统计信息
3. **数据质量** - 问题和建议
4. **关键发现** - 有价值的洞察
5. **后续建议** - 推荐的分析方向

### 示例输出
见 [examples/output-sample.md](../examples/output-sample.md)
```

## 6. 约束条件 (Constraints)

边界和限制：

```markdown
## 约束条件

### 能力边界
- 最大支持 100MB 数据文件
- 不处理图片/视频等非结构化数据
- 不执行修改数据的操作

### 安全约束
- 不在输出中暴露敏感数据样本
- 不连接外部网络
- 遵循数据脱敏规则

### 质量要求
- 所有统计数据需可验证
- 不做无依据的推断
- 明确标注不确定性
```

## 组件关系图

```
┌──────────────────────────────────────────────┐
│                  Metadata                     │
│            (识别和管理 Skill)                 │
└──────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│                  Trigger                      │
│              (决定何时启动)                   │
└──────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│                  Context                      │
│             (收集必要信息)                    │
└──────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│                   Logic                       │
│              (执行核心任务)                   │
│                     │                         │
│    ┌────────────────┼────────────────┐       │
│    │                │                │       │
│    ▼                ▼                ▼       │
│ Step 1          Step 2           Step N      │
└──────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│                  Output                       │
│             (标准化输出)                      │
│                     │                         │
│        Constraints (约束校验)                 │
└──────────────────────────────────────────────┘
```

## 实战写作技巧（来自 myclaude 项目洞察）

### SKILL.md 标准文档结构

```markdown
---
name: skill-name
description: 一句话说明什么时候用（核心）
---

# [Skill Name] Integration

## Overview
[简要说明功能]

## When to Use
[明确使用场景 - 这是最重要的部分]

## Usage
[具体调用方式]

## Parameters
[参数说明，用表格]

## Return Format
[输出格式，用代码块精确展示]

## Invocation Pattern
[调用模式，包括 Bash tool 参数]

## Examples
[从简单到复杂的示例]

## Notes
[补充说明]
```

### 写作核心原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **场景优先** | When to Use 是最重要的部分 | "Complex reasoning tasks requiring advanced AI" |
| **格式明确** | 输入输出格式必须精确 | 返回格式用代码块展示 |
| **示例驱动** | 从简单到复杂的示例 | Basic → With params → Advanced |
| **约束前置** | 关键限制要突出 | timeout: 7200000 (non-negotiable) |

### 关键技巧

**技巧一：Invocation Pattern 定死调用方式**

```yaml
Bash tool parameters:
- command: skill-wrapper - [working_dir] <<'EOF'
  <task content>
  EOF
- timeout: 7200000
- description: <brief description>
```

**技巧二：Return Format 结构化**

```markdown
### Return Format

正常输出：
```
Response text...

---
SESSION_ID: 019a7247-xxx
```

错误输出 (stderr)：
```
ERROR: Error message
```
```

**技巧三：Examples 覆盖三种场景**

```markdown
**Basic (最简单):**
command "simple task"

**Multiline (复杂输入):**
command <<'EOF'
multiline content
EOF

**Resume (高级用法):**
command resume <session_id> "continue"
```

## 下一步

阅读 [03-skills-integration.md](03-skills-integration.md) 了解各部分如何联动。
