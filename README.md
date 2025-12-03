# My Claude Code Workflow

个人 Claude Code 配置和 Skills 集合。

## 目录结构

```
.claude/
├── *.md                # 全局配置文档 (RULES, COMMANDS, MODES 等)
├── skills/             # 自定义 Skills
├── agents/             # 自定义 Agents
├── commands/           # 自定义命令
├── hooks/              # 钩子脚本
└── output-styles/      # 输出样式
```

## 使用方式

```bash
# 克隆到 ~/.claude
git clone https://github.com/GalaxyXieyu/claude-workflow.git ~/.claude

# 手动创建敏感配置文件
cp settings.example.json settings.json
# 编辑 settings.json 填入你的 API Key
```

## 敏感文件 (已忽略)

以下文件包含敏感信息，需要手动创建：

- `settings.json` - API Key 和环境变量
- `settings.local.json` - 本地权限配置
- `config.json` - 主 API Key
