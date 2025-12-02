# 数据探索 Skill

**动态探索**项目数据层，AI 自己决定怎么搜索。

## 目录结构

```
data-explorer-skill/
├── SKILL.md                    # 探索流程定义
├── scripts/
│   └── extract_schema.py       # 数据库 schema 提取（唯一需要的脚本）
└── references/
    └── schema/                 # 探索后缓存的 schema
```

## 核心思路

1. 用户给需求 + 项目路径
2. AI 用 grep/find 自己探索，不用预设脚本
3. 找到现有工具就用，没有再写
4. 需要 schema 时用 extract_schema.py 提取

## extract_schema.py 用法

```bash
# PostgreSQL
python extract_schema.py -t pg -H localhost -d mydb -u user -P pass -o ./schema/

# MySQL
python extract_schema.py -t mysql -H localhost -d mydb -u user -P pass -o ./schema/

# 达梦
python extract_schema.py -t dm -H localhost -d mydb -u user -P pass -o ./schema/

# Neo4j
python extract_schema.py -t neo4j -H localhost -u neo4j -P pass -o ./schema/

# Milvus
python extract_schema.py -t milvus -H localhost -o ./schema/

# Elasticsearch
python extract_schema.py -t es -H localhost -o ./schema/
```

输出：`{type}_schema.md` + `{type}_schema.json`
