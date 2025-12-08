# 列出所有 Skills

扫描并列出 `~/.claude/skills/` 目录下的所有 Skills。

## 执行步骤

1. 运行命令：
```bash
python3 ~/.claude/skills/skill-builder/scripts/skill-manager.py list -v
```

2. 解析输出，展示给用户：
   - Skill 名称
   - 描述
   - 版本数量

3. 分析覆盖情况，给出建议
