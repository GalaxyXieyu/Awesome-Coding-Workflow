#!/bin/bash
# 探索项目中的数据源配置
# 用法: ./find_datasources.sh <project_path>

PROJECT_PATH="${1:-.}"

echo "=== 探索数据源配置 ==="
echo "项目路径: $PROJECT_PATH"
echo ""

# 1. 查找环境变量文件
echo "### 环境变量文件"
find "$PROJECT_PATH" -maxdepth 3 -name ".env*" -o -name "*.env" 2>/dev/null | head -20

# 2. 查找配置文件
echo ""
echo "### 配置文件"
find "$PROJECT_PATH" -maxdepth 4 \( -name "*.yaml" -o -name "*.yml" -o -name "*.toml" -o -name "settings*.py" -o -name "config*.py" \) 2>/dev/null | grep -v node_modules | grep -v __pycache__ | head -30

# 3. 从配置中提取数据库关键词
echo ""
echo "### 数据库相关配置"
grep -r -l -i "database\|mysql\|postgres\|redis\|milvus\|neo4j\|elasticsearch\|mongodb" "$PROJECT_PATH" --include="*.py" --include="*.yaml" --include="*.yml" --include="*.env*" 2>/dev/null | grep -v __pycache__ | head -20

# 4. 查找 ORM/数据库连接代码
echo ""
echo "### 数据库连接代码"
grep -r -l "create_engine\|asyncpg\|pymysql\|psycopg\|pymilvus\|neo4j\|elasticsearch" "$PROJECT_PATH" --include="*.py" 2>/dev/null | grep -v __pycache__ | head -20

echo ""
echo "=== 探索完成 ==="
