# Claude Code Skills 项目 Makefile

.PHONY: help install install-global install-examples init-local clean

# 默认目标
help:
	@echo "Claude Code Skills 项目命令"
	@echo ""
	@echo "使用方法: make [target]"
	@echo ""
	@echo "目标:"
	@echo "  install         安装全部内容到全局目录"
	@echo "  install-global  仅安装模板到全局目录"
	@echo "  install-examples 安装示例 Skills"
	@echo "  init-local      初始化本地项目 Skills 目录"
	@echo "  clean           清理安装"
	@echo "  help            显示帮助"

# 安装全部
install:
	@chmod +x scripts/install.sh
	@./scripts/install.sh --all

# 安装全局模板
install-global:
	@chmod +x scripts/install.sh
	@./scripts/install.sh --global

# 安装示例
install-examples:
	@chmod +x scripts/install.sh
	@./scripts/install.sh --examples

# 初始化本地目录
init-local:
	@chmod +x scripts/install.sh
	@./scripts/install.sh --local

# 清理
clean:
	@echo "清理安装的文件..."
	@rm -rf ~/.claude/skills/basic-skill.md
	@rm -rf ~/.claude/skills/advanced-skill.md
	@rm -rf ~/.claude/skills/examples
	@echo "清理完成"
