#!/bin/bash

# Claude Code Skills 安装脚本
# 用法: ./install.sh [options]
# 选项:
#   --global    安装到全局 Skills 目录
#   --examples  同时安装示例 Skills
#   --all       安装所有内容

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
GLOBAL_SKILLS_DIR="$HOME/.claude/skills"
GLOBAL_RULES_DIR="$HOME/.claude/rules"
LOCAL_SKILLS_DIR=".claude/skills"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 创建目录
ensure_dir() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        log_info "创建目录: $1"
    fi
}

# 安装模板到全局目录
install_global() {
    log_info "安装到全局 Skills 目录..."
    ensure_dir "$GLOBAL_SKILLS_DIR"
    
    # 复制模板
    if [ -d "$PROJECT_DIR/templates" ]; then
        cp -r "$PROJECT_DIR/templates/"* "$GLOBAL_SKILLS_DIR/"
        log_info "模板已安装到 $GLOBAL_SKILLS_DIR"
    fi
}

# 安装示例
install_examples() {
    log_info "安装示例 Skills..."
    ensure_dir "$GLOBAL_SKILLS_DIR/examples"
    
    if [ -d "$PROJECT_DIR/examples" ]; then
        cp -r "$PROJECT_DIR/examples/"* "$GLOBAL_SKILLS_DIR/examples/"
        log_info "示例已安装到 $GLOBAL_SKILLS_DIR/examples"
    fi
}

# 初始化项目本地 Skills 目录
init_local() {
    log_info "初始化本地 Skills 目录..."
    ensure_dir "$LOCAL_SKILLS_DIR"
    
    # 创建 .gitkeep
    touch "$LOCAL_SKILLS_DIR/.gitkeep"
    log_info "本地 Skills 目录已创建: $LOCAL_SKILLS_DIR"
}

# 显示帮助
show_help() {
    echo "Claude Code Skills 安装脚本"
    echo ""
    echo "用法: ./install.sh [选项]"
    echo ""
    echo "选项:"
    echo "  --global    安装模板到全局 Skills 目录"
    echo "  --examples  安装示例 Skills"
    echo "  --local     初始化本地项目 Skills 目录"
    echo "  --all       安装所有内容"
    echo "  --help      显示帮助"
    echo ""
    echo "示例:"
    echo "  ./install.sh --all       # 安装全部"
    echo "  ./install.sh --global    # 仅安装全局模板"
}

# 验证安装
verify_installation() {
    log_info "验证安装..."
    
    local success=true
    
    if [ -d "$GLOBAL_SKILLS_DIR" ]; then
        log_info "全局 Skills 目录: OK"
    else
        log_warn "全局 Skills 目录不存在"
        success=false
    fi
    
    if [ -d "$LOCAL_SKILLS_DIR" ]; then
        log_info "本地 Skills 目录: OK"
    else
        log_warn "本地 Skills 目录不存在"
    fi
    
    if $success; then
        log_info "安装验证完成"
    fi
}

# 主函数
main() {
    echo "========================================"
    echo " Claude Code Skills 安装程序"
    echo "========================================"
    echo ""
    
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    local do_global=false
    local do_examples=false
    local do_local=false
    
    for arg in "$@"; do
        case $arg in
            --global)
                do_global=true
                ;;
            --examples)
                do_examples=true
                ;;
            --local)
                do_local=true
                ;;
            --all)
                do_global=true
                do_examples=true
                do_local=true
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知选项: $arg"
                show_help
                exit 1
                ;;
        esac
    done
    
    if $do_global; then
        install_global
    fi
    
    if $do_examples; then
        install_examples
    fi
    
    if $do_local; then
        init_local
    fi
    
    echo ""
    verify_installation
    
    echo ""
    log_info "安装完成"
    echo ""
    echo "下一步:"
    echo "  1. 阅读文档: docs/01-skills-basics.md"
    echo "  2. 查看示例: examples/data-exploration/"
    echo "  3. 使用模板创建自己的 Skill"
}

main "$@"
