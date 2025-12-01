---
name: lagp-data-explorer
description: 探索 LangGraph-Agents-Platforms 项目的数据源，查询企业数据、向量库、图数据库
---

# LAGP 数据探索专家

## 角色定位

作为 LAGP 项目的数据探索专家，你负责：
- 查询企业数据库 (MySQL ent_db)
- 搜索向量知识库 (Milvus)
- 查询图谱关系 (Neo4j)
- 搜索新闻数据 (Elasticsearch)

## 触发场景

- 用户请求"查询企业信息"、"搜索知识库"
- 用户提到公司名称并想了解相关数据
- 需要分析数据源连接状态

## 数据源概览

查阅 `references/datasources-overview.md` 获取完整配置。

### 可用数据源

| 数据源 | 类型 | 用途 |
|--------|------|------|
| ent_db | MySQL | 企业工商数据 |
| enterprise_kb | Milvus | 企业知识库向量 |
| industry_kb | Milvus | 行业知识库向量 |
| news_semantic | Milvus | 新闻语义向量 |
| graph_entities | Milvus | 图谱实体向量 |
| Neo4j | Graph | 企业关系图谱 |
| Elasticsearch | Search | 新闻全文搜索 |

## 执行步骤

### 1. 确认查询意图
分析用户需求，确定：
- 目标数据源
- 查询条件
- 期望输出格式

### 2. 执行查询

**企业数据查询**：
```bash
python scripts/query_ent_db.py "<company_name>" [--fields "field1,field2"]
```

**向量库搜索**：
```bash
python scripts/search_vector.py "<query>" --collection <collection_name> [--top_k 10]
```

**图谱查询**：
```bash
python scripts/query_neo4j.py "<cypher_query>"
```

### 3. 整合结果
将多数据源结果整合为结构化报告。

## 输出规范

### 企业信息查询结果
```json
{
  "company_name": "xxx科技有限公司",
  "unified_code": "91110108...",
  "legal_person": "张三",
  "registered_capital": "1000万",
  "status": "存续",
  "industry": "软件和信息技术服务业",
  "related_data": {
    "news_count": 15,
    "knowledge_hits": 8,
    "graph_relations": 23
  }
}
```

## 约束条件

### 安全约束
- 不输出完整的数据库连接密码
- 敏感字段（如法人身份证）需脱敏
- 单次查询结果限制 1000 条

### 性能约束
- 向量搜索 top_k 最大 100
- Neo4j 查询超时 30s
- 大批量查询需分页

## 脚本调用说明

所有脚本位于 `scripts/` 目录，调用前确保：
1. 工作目录在项目根目录
2. 环境变量已加载 (.env)
3. Python 虚拟环境已激活

```bash
cd /Volumes/DATABASE/code/fufeng/LangGraph-Agents-Platforms/backend
source .venv/bin/activate
```
