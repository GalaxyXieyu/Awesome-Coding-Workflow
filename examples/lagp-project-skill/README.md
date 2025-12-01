# LAGP 数据探索 Skill

针对 LangGraph-Agents-Platforms 项目的数据探索 Skill 示例。

## 目录结构

```
lagp-project-skill/
├── SKILL.md                          # 核心定义（大脑）
├── scripts/                          # 可执行脚本（双手）
│   ├── query_ent_db.py               # 企业库查询
│   ├── search_vector.py              # 向量库搜索
│   └── query_neo4j.py                # 图谱查询
├── references/                       # 参考文档（知识库）
│   └── datasources-overview.md       # 数据源配置说明
├── assets/                           # 资源文件（工具箱）
│   └── templates/
│       └── company_report.md         # 报告模板
└── README.md
```

## 使用方式

### 1. 部署到 Claude 配置目录

```bash
cp -r lagp-project-skill ~/.claude/skills/
```

### 2. 脚本调用示例

```bash
# 查询企业信息
python scripts/query_ent_db.py "腾讯" --limit 5

# 向量搜索
python scripts/search_vector.py "人工智能技术" --collection enterprise_kb --top_k 10

# 图谱查询
python scripts/query_neo4j.py "company_relations" --params '{"company_name": "腾讯"}'
```

## 适配你的项目

1. 修改 `references/datasources-overview.md` 中的配置信息
2. 调整 `scripts/` 中的数据库连接逻辑
3. 更新 `SKILL.md` 中的角色定义和执行步骤
