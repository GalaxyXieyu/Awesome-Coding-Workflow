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

## 下一步

阅读 [06-skills-evaluation.md](06-skills-evaluation.md) 了解效果评估指标。
