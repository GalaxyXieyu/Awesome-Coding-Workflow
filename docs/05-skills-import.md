# 导入引用方法

## Skills 存储位置

### 全局 Skills

```bash
~/.claude/skills/
├── data-exploration.md
├── code-review.md
└── api-documentation.md
```

所有项目可用。

### 项目 Skills

```bash
.claude/skills/
├── project-specific.md
└── domain-skill.md
```

仅当前项目可用。

## 导入方式

### 方式一：文件直接放置

最简单的方式，直接将 Skill 文件放入对应目录：

```bash
# 全局安装
cp my-skill.md ~/.claude/skills/

# 项目安装
cp my-skill.md .claude/skills/
```

### 方式二：符号链接

适合管理多个项目共享的 Skills：

```bash
# 创建 Skills 仓库
mkdir ~/my-skills
cd ~/my-skills
git init

# 在项目中创建链接
ln -s ~/my-skills/data-exploration.md .claude/skills/
```

### 方式三：Git Submodule

适合团队共享 Skills：

```bash
# 添加 submodule
git submodule add https://github.com/team/shared-skills .claude/shared-skills

# 更新
git submodule update --remote
```

### 方式四：脚本安装

```bash
# 使用安装脚本
curl -fsSL https://example.com/install-skills.sh | bash

# 或使用 Make
make install-skills
```

## 引用语法

### 在 Skill 中引用其他 Skill

```markdown
# 复合 Skill

## 依赖
- `@skill/data-exploration` - 数据探索
- `@skill/data-cleaning` - 数据清洗

## 执行流程
1. 调用 `data-exploration` 分析数据
2. 根据分析结果调用 `data-cleaning`
3. 整合输出
```

### 在 Rules 中引用 Skill

```markdown
# 项目规则

## 数据处理规范
当处理数据时，必须先使用 `@skill/data-validation` 验证数据质量
```

## 版本管理

### 版本号规范

```
skill-name@version
skill-name@1.0.0
skill-name@latest
```

### 版本锁定

在项目中创建 `.claude/skills.lock`：

```yaml
skills:
  data-exploration:
    version: "1.2.0"
    source: "github:user/repo"
  code-review:
    version: "2.0.0"
    source: "local"
```

## 远程 Skills

### 从 GitHub 安装

```bash
# 使用脚本
claude-skill install github:user/repo/skill-name

# 或手动下载
curl -o ~/.claude/skills/skill-name.md \
  https://raw.githubusercontent.com/user/repo/main/skills/skill-name.md
```

### 从 Registry 安装

```bash
# 假设存在 Skills registry
claude-skill install @official/data-exploration
```

## 组织结构建议

### 个人项目

```
~/.claude/
├── rules/
│   └── global.md           # 全局规则
└── skills/
    ├── personal/           # 个人常用
    │   ├── quick-debug.md
    │   └── code-review.md
    └── domain/             # 领域特定
        ├── react-component.md
        └── api-design.md
```

### 团队项目

```
project/
├── .claude/
│   ├── rules/
│   │   └── team-standards.md
│   ├── skills/
│   │   └── project-specific.md
│   └── shared-skills/         # git submodule
│       ├── data-exploration.md
│       └── code-review.md
└── src/
```

## 导入最佳实践

### 1. 命名规范

```
# 好的命名
data-exploration.md
react-component-generator.md
api-documentation.md

# 避免的命名
skill1.md
my-skill.md
test.md
```

### 2. 依赖声明

在 Skill 文件头部声明依赖：

```markdown
---
name: complex-analysis
dependencies:
  - data-exploration@^1.0
  - data-cleaning@^2.0
---
```

### 3. 冲突处理

当全局和项目存在同名 Skill 时：
- **默认**：项目级优先
- **显式引用**：`@global/skill-name` 或 `@project/skill-name`

### 4. 更新策略

```bash
# 检查更新
claude-skill outdated

# 更新特定 skill
claude-skill update data-exploration

# 更新全部
claude-skill update --all
```

## 脚本封装（来自 myclaude 项目洞察）

### Skill 目录结构模式

```
skills/
├── codex/                    # Skill 模块
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

### 脚本与提示词的关系

```
SKILL.md (提示词)  ←→  scripts/*.py (执行器)
     ↓                      ↓
  告诉 Claude              实际执行
  什么时候调用              封装 CLI 调用
  怎么调用                  处理输入输出
```

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

DEFAULT_MODEL = os.environ.get('MODEL', 'default')
DEFAULT_TIMEOUT = 7200  # 2小时

def log_error(msg): sys.stderr.write(f"ERROR: {msg}\n")
def log_warn(msg): sys.stderr.write(f"WARN: {msg}\n")
def log_info(msg): sys.stderr.write(f"INFO: {msg}\n")

def parse_args():
    if len(sys.argv) < 2:
        log_error('Task required')
        sys.exit(1)
    return {'task': sys.argv[1], 'workdir': sys.argv[2] if len(sys.argv) > 2 else '.'}

def build_cli_args(params) -> list:
    return ['cli', '-m', DEFAULT_MODEL, params['task']]

def run_process(args, timeout):
    try:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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

### 脚本调用方式

```bash
# 方式1: uv run (推荐)
uv run ~/.claude/skills/gemini/scripts/gemini.py "prompt"

# 方式2: 直接执行
~/.claude/skills/gemini/scripts/gemini.py "prompt"

# 方式3: python 调用
python3 ~/.claude/skills/gemini/scripts/gemini.py "prompt"
```

### 脚本必须处理的事项

- [ ] 参数解析和验证
- [ ] 超时控制 (默认 2 小时)
- [ ] 错误处理 (FileNotFoundError, TimeoutExpired, KeyboardInterrupt)
- [ ] 输出规范化
- [ ] 日志分级 (INFO/WARN/ERROR 到 stderr)

## 下一步

阅读 [06-skills-evaluation.md](06-skills-evaluation.md) 了解效果评估指标。
