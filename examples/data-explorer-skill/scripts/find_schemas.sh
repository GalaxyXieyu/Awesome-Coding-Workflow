#!/bin/bash
# 探索项目中的数据模型/Schema 定义
# 用法: ./find_schemas.sh <project_path>

PROJECT_PATH="${1:-.}"

echo "=== 探索数据模型 ==="
echo "项目路径: $PROJECT_PATH"
echo ""

# 1. 查找 SQLAlchemy 模型
echo "### SQLAlchemy 模型"
grep -r -l "Base\|declarative_base\|Column\|relationship" "$PROJECT_PATH" --include="*.py" 2>/dev/null | grep -v __pycache__ | grep -i "model\|schema\|entity" | head -20

# 2. 查找 Pydantic 模型
echo ""
echo "### Pydantic 模型"
grep -r -l "BaseModel\|Field\|validator" "$PROJECT_PATH" --include="*.py" 2>/dev/null | grep -v __pycache__ | grep -i "schema\|dto\|model" | head -20

# 3. 查找 SQL 文件
echo ""
echo "### SQL Schema 文件"
find "$PROJECT_PATH" -name "*.sql" -o -name "*schema*" -o -name "*migration*" 2>/dev/null | grep -v node_modules | head -20

# 4. 查找 domain/entity 目录
echo ""
echo "### Domain/Entity 目录"
find "$PROJECT_PATH" -type d \( -name "domain" -o -name "entity" -o -name "entities" -o -name "models" \) 2>/dev/null | grep -v node_modules | grep -v __pycache__ | head -10

# 5. 查找向量库 collection 定义
echo ""
echo "### 向量库 Collection 定义"
grep -r -l "Collection\|collection_name\|create_collection" "$PROJECT_PATH" --include="*.py" --include="*.yaml" 2>/dev/null | grep -v __pycache__ | head -10

echo ""
echo "=== 探索完成 ==="
