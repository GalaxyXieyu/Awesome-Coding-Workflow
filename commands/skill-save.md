# 保存 Skill 版本

保存指定 Skill 的当前版本到历史记录。

## 参数

- `$ARGUMENTS`: Skill 名称 [版本消息]

## 执行步骤

1. 保存版本：
```bash
python3 ~/.claude/skills/skill-builder/scripts/skill-manager.py save $ARGUMENTS
```

2. 确认保存成功

3. 提示用户可以用 `/skill-history` 查看历史
