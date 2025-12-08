# Plugins Marketplace 使用与维护指南

## 概述

Claude Code 的 Plugins 支持通过 Git 仓库分享和安装，形成完整的闭环：

```
社区仓库 → Fork → 本地定制 → 推送到团队仓库 → 团队成员安装
    ↑                                              ↓
    ←←←←←←← 贡献回上游（PR） ←←←←←←←←←←←←←←←←←←←←←←
```

---

## 场景 A：纯使用（不改动）

直接安装，享受更新：

```shell
# 1. 添加 marketplace（推荐：cexll/myclaude 是一个功能强大的插件集合）
/plugin marketplace add https://github.com/cexll/myclaude.git

# 2. 安装插件
/plugin install myclaude

# 3. 后续更新（作者更新后）
/plugin install myclaude  # 重新安装即可获取最新版
```

**适合**：只想用，不想改

---

## 场景 B：维护/定制（需要 Fork）

想修改或贡献，必须 Fork：

```bash
# 1. Fork 到自己的 GitHub（网页操作）
# https://github.com/cexll/myclaude → Fork → https://github.com/your-org/myclaude

# 2. Clone 到本地
git clone https://github.com/your-org/myclaude.git
cd myclaude

# 3. 修改定制
# 编辑插件...

# 4. 推送
git add .
git commit -m "定制 xxx 插件"
git push

# 5. 团队成员安装（用你 Fork 后的地址）
/plugin marketplace add https://github.com/your-org/myclaude.git
/plugin install myclaude
```

**适合**：想定制、想贡献、想团队共享私有修改

---

## 场景 C：从零创建 Plugins 仓库

### 1. 初始化仓库

```bash
mkdir my-claude-plugins && cd my-claude-plugins
git init
```

### 2. 创建 marketplace 配置

```bash
mkdir -p .claude-plugin
```

创建 `.claude-plugin/marketplace.json`：

```json
{
  "name": "my-plugins",
  "description": "我的 Claude Code 插件集合",
  "plugins": [
    {
      "name": "my-first-plugin",
      "description": "插件描述",
      "path": "plugins/my-first-plugin"
    }
  ]
}
```

### 3. 创建插件目录结构

```
my-claude-plugins/
├── .claude-plugin/
│   └── marketplace.json      # marketplace 配置
├── plugins/
│   └── my-first-plugin/
│       ├── plugin.json       # 插件元数据
│       ├── README.md         # 插件说明
│       └── commands/         # 命令定义
│           └── example.md
└── README.md                 # 仓库说明
```

### 4. 创建插件元数据

`plugins/my-first-plugin/plugin.json`：

```json
{
  "name": "my-first-plugin",
  "version": "1.0.0",
  "description": "插件描述",
  "commands": ["commands/example.md"]
}
```

### 5. 推送到 GitHub

```bash
git add .
git commit -m "Initial plugins"
git remote add origin https://github.com/your-org/my-claude-plugins.git
git push -u origin main
```

### 6. 使用

```shell
/plugin marketplace add your-org/my-claude-plugins
/plugin install my-first-plugin
```

---

## 维护流程

### 更新插件

```bash
# 修改插件内容
git add .
git commit -m "Update: 描述修改内容"
git push
```

### 用户获取更新

```shell
# 重新安装即可
/plugin install my-first-plugin
```

### 同步上游更新（Fork 场景）

```bash
# 添加上游仓库
git remote add upstream https://github.com/cexll/myclaude.git

# 拉取上游更新
git fetch upstream
git merge upstream/main

# 推送到自己的仓库
git push
```

---

## 快速参考

| 我想... | 操作 |
|---------|------|
| **直接用** | `/plugin marketplace add` + `/plugin install` |
| **改一改再用** | Fork → Clone → 修改 → Push → 团队 add 你的仓库 |
| **从零创建** | 创建仓库 + marketplace.json + 插件目录 |
| **同步上游** | `git remote add upstream` + `git fetch` + `git merge` |
| **更新插件** | 修改 → `git push` → 用户重新 `/plugin install` |
