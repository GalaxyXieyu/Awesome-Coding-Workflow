#!/bin/bash
# Skills Library MCP 启动脚本

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LIBRARY_MCP_DIR="$HOME/library-mcp"
SKILLS_DIR="$HOME/.claude/skills"
UV_PATH="$HOME/.local/bin/uv"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Skills Library MCP 配置生成器${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查依赖
if [ ! -f "$UV_PATH" ]; then
    echo "❌ uv 未安装，请先运行: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if [ ! -d "$LIBRARY_MCP_DIR" ]; then
    echo "❌ library-mcp 未安装，正在克隆..."
    git clone https://github.com/lethain/library-mcp.git "$LIBRARY_MCP_DIR"
fi

if [ ! -d "$SKILLS_DIR" ]; then
    echo "❌ skills 目录不存在: $SKILLS_DIR"
    exit 1
fi

# 预安装依赖
echo "📦 检查依赖..."
cd "$LIBRARY_MCP_DIR" && $UV_PATH sync --quiet 2>/dev/null

echo -e "${GREEN}✅ 依赖就绪${NC}"
echo ""

# 生成配置
echo -e "${BLUE}📋 复制以下配置到 cc-switch:${NC}"
echo ""
echo "========== cc-switch JSON 配置 =========="
cat << EOF
{
  "skills-library": {
    "command": "$UV_PATH",
    "args": [
      "--directory",
      "$LIBRARY_MCP_DIR",
      "run",
      "main.py",
      "$SKILLS_DIR"
    ],
    "type": "stdio"
  }
}
EOF
echo "=========================================="
echo ""

# Windsurf/Cursor 格式
echo -e "${BLUE}📋 或者 Windsurf/Cursor mcp.json 格式:${NC}"
echo ""
cat << EOF
"skills-library": {
    "args": [
        "--directory",
        "$LIBRARY_MCP_DIR",
        "run",
        "main.py",
        "$SKILLS_DIR"
    ],
    "command": "$UV_PATH",
    "type": "stdio"
}
EOF
echo ""

# 测试运行
echo -e "${BLUE}🧪 测试 MCP 是否正常...${NC}"
cd "$LIBRARY_MCP_DIR"
RESULT=$($UV_PATH run python -c "
import main
mgr = main.HugoContentManager(['$SKILLS_DIR'])
tags = mgr.list_all_tags()
print(f'✅ 成功加载 {len(tags)} 个 tags')
for tag, count, _ in tags[:5]:
    print(f'   - {tag}: {count} files')
" 2>&1)

echo "$RESULT"
echo ""
echo -e "${GREEN}🎉 配置完成！复制上面的 JSON 到 cc-switch 即可${NC}"
