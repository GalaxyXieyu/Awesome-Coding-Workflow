# myclaude Skills 精华洞察

> 来源分析：https://github.com/cexll/myclaude/tree/master/skills

## 核心发现

### Skills 目录结构模式

```
skills/
├── codex/                    # 某个能力模块
│   ├── SKILL.md              # 提示词定义
│   └── scripts/
│       └── codex.py          # 执行脚本
└── gemini/
    ├── SKILL.md
    └── scripts/
        └── gemini.py
```

**关键点**：
- 每个 Skill 是一个独立目录
- `SKILL.md` 定义提示词和使用说明
- `scripts/` 存放实际执行脚本
- 命名一致：目录名 = 脚本名

---

## 提示词怎么写

### 1. 标准 YAML 头部

```yaml
---
name: gemini
description: Execute Gemini CLI for AI-powered code analysis and generation. Use when you need to leverage Google's Gemini models for complex reasoning tasks.
---
```

**要素**：
- `name`: 短标识符
- `description`: 一句话说明 **什么时候用**

### 2. 文档结构模板

```markdown
# [Skill Name] Integration

## Overview
[简要说明功能]

## When to Use
[明确使用场景，这是核心]

## Usage
[具体调用方式]

## Environment Variables
[可配置项]

## Timeout Control
[超时处理]

## Parameters
[参数说明]

## Return Format
[输出格式]

## Invocation Pattern
[调用模式，包括 Bash tool 参数]

## Examples
[具体示例，从简单到复杂]

## Notes
[补充说明]
```

### 3. 提示词写作核心原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **场景优先** | 先说 When to Use | "Complex reasoning tasks requiring advanced AI" |
| **格式明确** | 输入输出格式必须精确 | 返回格式用代码块展示 |
| **示例驱动** | 从简单到复杂的示例 | Basic → With params → Advanced |
| **约束前置** | 关键限制要突出 | timeout: 7200000 (non-negotiable) |

### 4. 关键写法技巧

**技巧一：Invocation Pattern 定死调用方式**

```markdown
### Invocation Pattern

All automated executions must use HEREDOC syntax through the Bash tool:

```yaml
Bash tool parameters:
- command: codex-wrapper - [working_dir] <<'EOF'
  <task content>
  EOF
- timeout: 7200000
- description: <brief description>
```
```

**技巧二：Return Format 结构化**

```markdown
### Return Format

```
Agent response text here...

---
SESSION_ID: 019a7247-ac9d-71f3-89e2-a823dbd8fd14
```

Error format (stderr):
```
ERROR: Error message
```
```

**技巧三：用 Examples 覆盖所有场景**

```markdown
### Examples

**Basic (最简单的情况):**
```bash
command "simple task"
```

**With multiline (复杂输入):**
```bash
command <<'EOF'
multiline
content
EOF
```

**Resume session (高级用法):**
```bash
command resume <session_id> "continue task"
```
```

---

## 脚本是怎么用的

### 脚本的作用

```
SKILL.md (提示词)  ←→  scripts/*.py (执行器)
     ↓                      ↓
  告诉 Claude              实际执行
  什么时候调用              封装 CLI 调用
  怎么调用                  处理输入输出
```

### 脚本核心功能

1. **CLI 封装** - 将复杂的命令行工具简化为统一接口
2. **参数处理** - 解析和验证输入
3. **输出规范化** - 统一输出格式
4. **错误处理** - 超时、异常、中断
5. **状态管理** - session_id、resume

### 脚本标准模式

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import subprocess
import sys
import os

# 配置常量
DEFAULT_MODEL = os.environ.get('MODEL', 'default')
DEFAULT_TIMEOUT = 7200  # 2小时

def log_error(msg): sys.stderr.write(f"ERROR: {msg}\n")
def log_warn(msg): sys.stderr.write(f"WARN: {msg}\n")
def log_info(msg): sys.stderr.write(f"INFO: {msg}\n")

def parse_args():
    """解析命令行参数"""
    if len(sys.argv) < 2:
        log_error('Task required')
        sys.exit(1)
    return {'task': sys.argv[1], 'workdir': sys.argv[2] if len(sys.argv) > 2 else '.'}

def build_cli_args(params) -> list:
    """构建 CLI 参数"""
    return ['cli', '-m', DEFAULT_MODEL, params['task']]

def run_process(args, timeout):
    """执行子进程"""
    try:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # 处理输出...
        returncode = process.wait(timeout=timeout)
        if returncode != 0:
            log_error(f'Exit status {returncode}')
            sys.exit(returncode)
    except subprocess.TimeoutExpired:
        log_error('Timeout')
        process.kill()
        sys.exit(124)
    except FileNotFoundError:
        log_error('Command not found')
        sys.exit(127)

def main():
    params = parse_args()
    args = build_cli_args(params)
    run_process(args, DEFAULT_TIMEOUT)

if __name__ == '__main__':
    main()
```

### 调用方式

```bash
# 方式1: uv run (推荐，自动管理依赖)
uv run ~/.claude/skills/gemini/scripts/gemini.py "prompt"

# 方式2: 直接执行
~/.claude/skills/gemini/scripts/gemini.py "prompt"

# 方式3: python 调用
python3 ~/.claude/skills/gemini/scripts/gemini.py "prompt"
```

---

## 什么时候要封装脚本

### 需要封装脚本的场景

| 场景 | 原因 | 示例 |
|------|------|------|
| **CLI 工具复杂** | 参数多、输出格式乱 | codex CLI 输出 JSON 流 |
| **需要输出规范化** | 原始输出不适合 AI 消费 | 提取 agent_message |
| **需要状态管理** | session、resume | 返回 SESSION_ID |
| **需要超时控制** | 长时间运行任务 | 2小时超时保护 |
| **需要错误处理** | 优雅降级 | 命令不存在、超时、中断 |
| **跨平台兼容** | Windows/Mac/Linux | Python 标准库实现 |

### 不需要封装脚本的场景

| 场景 | 原因 |
|------|------|
| **CLI 简单直接** | 直接在 SKILL.md 写命令即可 |
| **输出已规范** | 不需要额外处理 |
| **无状态任务** | 一次性执行，无需 resume |
| **内置工具** | 使用 Claude 已有能力 |

### 封装决策流程

```
是否封装脚本？
    │
    ├── CLI 输出需要解析/转换？ → 是 → 封装
    │
    ├── 需要 session/状态管理？ → 是 → 封装
    │
    ├── 需要复杂错误处理？ → 是 → 封装
    │
    ├── 参数需要复杂验证？ → 是 → 封装
    │
    └── 以上都否 → 直接在 SKILL.md 写命令
```

---

## 高级模式洞察

### 1. HEREDOC 模式处理复杂输入

```bash
# 问题：引号、特殊字符、多行文本
codex-wrapper - <<'EOF'
Fix the bug where regex /\d+/ doesn't match
The $variable should be escaped
EOF
```

**核心点**：`<<'EOF'` 保持原样，不进行 shell 解释

### 2. 并行执行模式

```bash
codex-wrapper --parallel - <<'EOF'
---TASK---
id: analyze_1732876800
workdir: /project
---CONTENT---
analyze requirements
---TASK---
id: implement_1732876801
dependencies: analyze_1732876800
---CONTENT---
implement based on analysis
EOF
```

**核心点**：
- 任务间依赖用 `dependencies` 声明
- 单次调用完成多阶段工作流
- 自动拓扑排序

### 3. Session Resume 模式

```bash
# 首次执行
codex-wrapper - <<'EOF'
add comments to utils.js
EOF
# 输出 SESSION_ID: 019a7247-xxx

# 继续对话
codex-wrapper resume 019a7247-xxx - <<'EOF'
now add TypeScript types
EOF
```

**核心点**：保持上下文，支持增量任务

---

## 总结：Skill 设计清单

### SKILL.md 必须包含

- [ ] YAML 头部 (name, description)
- [ ] When to Use 明确场景
- [ ] Usage 调用方式
- [ ] Parameters 参数说明
- [ ] Return Format 输出格式
- [ ] Invocation Pattern 调用模式
- [ ] Examples 覆盖常见场景

### 脚本必须处理

- [ ] 参数解析和验证
- [ ] 超时控制 (默认 2 小时)
- [ ] 错误处理 (FileNotFoundError, TimeoutExpired, KeyboardInterrupt)
- [ ] 输出规范化
- [ ] 日志分级 (INFO/WARN/ERROR 到 stderr)

### 封装判断

- [ ] CLI 输出是否需要解析？
- [ ] 是否需要状态管理？
- [ ] 是否需要复杂错误处理？
- [ ] 是否涉及长时间运行？
