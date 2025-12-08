# 查看 Skill 版本历史

查看指定 Skill 的版本历史，支持回滚。

## 参数

- `$ARGUMENTS`: Skill 名称

## 执行步骤

1. 查看版本历史：
```bash
python3 ~/.claude/skills/skill-builder/scripts/skill-manager.py history $ARGUMENTS
```

2. 如果用户要回滚，执行：
```bash
python3 ~/.claude/skills/skill-builder/scripts/skill-manager.py rollback $ARGUMENTS <版本号>
```

3. 确认回滚结果
