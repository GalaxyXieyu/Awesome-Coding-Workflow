# 把 Skills 带到 Windsurf：一次配置，多 IDE 共享

## 痛点

你花了大量时间打磨的 Claude Code Skills，只能在 Claude Code 里用？

换到 Windsurf、Cursor 就得从零开始？

**不用。**

通过 MCP（Model Context Protocol），你的 Skills 可以像"知识库"一样暴露出来，任何支持 MCP 的 AI 工具都能访问。

---

## 原理

```
你的 Skills 目录（~/.claude/skills/）
        ↓
   library-mcp（MCP 服务器）
        ↓
  ┌─────┼─────┐
  ↓     ↓     ↓
Claude  Windsurf  Cursor
Code    (Cascade) (AI)
```

**一份 Skills，多处使用。**

---

## 3 分钟配置

### 第 1 步：安装依赖

```bash
# 安装 uv（Python 包管理器，比 pip 快 10 倍）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆 library-mcp（MCP 服务器）
git clone https://github.com/lethain/library-mcp.git ~/library-mcp
```

### 第 2 步：确保 Skills 有 tags

`library-mcp` 通过 `tags` 字段索引内容。**没有 tags 的文件不会被发现。**

检查你的 `SKILL.md`：

```yaml
---
name: my-skill
description: 技能描述
tags:           # 必须有这个！
  - tag1
  - tag2
---
```

### 第 3 步：一键生成配置

```bash
~/.claude/mcp-skills/start.sh
```

会输出可直接复制的 JSON 配置：

```
========== cc-switch JSON 配置 ==========
{
  "skills-library": {
    "command": "/Users/xxx/.local/bin/uv",
    "args": [
      "--directory",
      "/Users/xxx/library-mcp",
      "run",
      "main.py",
      "/Users/xxx/.claude/skills"
    ],
    "type": "stdio"
  }
}
==========================================
```

### 第 4 步：粘贴到 IDE

#### Windsurf

编辑 `~/.codeium/windsurf/mcp_config.json`：

```json
{
  "mcpServers": {
    // 粘贴这里
  }
}
```

#### Cursor

编辑 `~/.cursor/mcp.json`：

```json
{
  "mcpServers": {
    // 粘贴这里
  }
}
```

#### cc-switch / Claude Code

直接粘贴到 MCP 配置文件。

---

## 验证成功

在 Windsurf/Cursor 对话中输入：

```
用 skills-library 的 list_all_tags 列出所有标签
```

如果返回标签列表 → 配置成功！

---

## 使用方式

配置成功后，AI 可以调用这些工具：

| 你想做什么 | 告诉 AI |
|----------|---------|
| 看有哪些技能 | "用 skills-library 列出所有 tags" |
| 找某个技能 | "用 skills-library 搜索 data 相关的技能" |
| 查看技能详情 | "用 skills-library 获取 codex 技能的内容" |

**AI 会自动调用对应的 MCP 工具，把你的 Skills 内容返回。**

---

## 常见问题

### Q: MCP 超时？

首次启动需要安装 Python 依赖，可能较慢。

**解决**：先运行 `~/.claude/mcp-skills/start.sh` 预安装依赖。

### Q: 返回空结果？

检查 SKILL.md 是否有 `tags` 字段。没有 tags 的文件不会被索引。

### Q: 找不到 uv？

```bash
# 确认安装
which uv  # 应该输出 ~/.local/bin/uv

# 如果没有，重新安装
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Q: 想加载多个目录？

在 args 中添加多个路径：

```json
"args": [
  "--directory", "/path/to/library-mcp",
  "run", "main.py",
  "/path/to/skills1",
  "/path/to/skills2"
]
```

---

## 总结

| 步骤 | 做什么 |
|------|--------|
| 1 | 安装 uv + 克隆 library-mcp |
| 2 | 确保 SKILL.md 有 tags |
| 3 | 运行 `start.sh` 生成配置 |
| 4 | 粘贴到 IDE 的 mcp 配置 |
| 5 | 重启 IDE，验证 |

**一次配置，所有 IDE 共享你的 Skills。**
