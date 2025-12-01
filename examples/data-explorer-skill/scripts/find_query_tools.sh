#!/bin/bash
# 探索项目中封装好的查询工具
# 用法: ./find_query_tools.sh <project_path>

PROJECT_PATH="${1:-.}"

echo "=== 探索查询工具 ==="
echo "项目路径: $PROJECT_PATH"
echo ""

# 1. 查找 Repository 类
echo "### Repository 类"
grep -r -l "Repository\|Repo\|DAO" "$PROJECT_PATH" --include="*.py" 2>/dev/null | grep -v __pycache__ | head -20

# 2. 查找 Service 类
echo ""
echo "### Service 类"
grep -r -l "Service\|UseCase" "$PROJECT_PATH" --include="*.py" 2>/dev/null | grep -v __pycache__ | grep -i "service\|application" | head -20

# 3. 查找 Agent Tools
echo ""
echo "### Agent Tools"
grep -r -l "@tool\|BaseTool\|StructuredTool\|def.*tool" "$PROJECT_PATH" --include="*.py" 2>/dev/null | grep -v __pycache__ | head -20

# 4. 查找查询函数
echo ""
echo "### 查询函数 (query/search/get/find)"
grep -r -l "def query\|def search\|def get_\|def find_\|def fetch" "$PROJECT_PATH" --include="*.py" 2>/dev/null | grep -v __pycache__ | grep -v test | head -20

# 5. 查找 infrastructure 层
echo ""
echo "### Infrastructure 层"
find "$PROJECT_PATH" -type d -name "infrastructure" 2>/dev/null | head -5
find "$PROJECT_PATH" -type d -name "repositories" 2>/dev/null | head -5

echo ""
echo "=== 探索完成 ==="
