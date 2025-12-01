# LAGP 数据源配置概览

## 配置文件位置

| 配置项 | 文件路径 |
|--------|----------|
| 环境变量 | `.env` |
| 数据源定义 | `src/infrastructure/config/datasources.yaml` |
| 模型配置 | `src/infrastructure/config/models.yaml` |
| 应用设置 | `src/infrastructure/config/settings.py` |

## MySQL 企业库 (ent_db)

```yaml
type: mysql
jdbc_url: jdbc:mysql://192.168.10.28:3306/nanshan_ent_qxb
username: cdusi
```

### 主要表结构

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| company_basic | 企业基本信息 | company_name, unified_code, legal_person |
| company_change | 变更记录 | change_date, change_item, before_value, after_value |
| company_shareholder | 股东信息 | shareholder_name, share_ratio |
| company_executive | 高管信息 | name, position |

## Milvus 向量库

**连接地址**: `192.168.10.206:19530`

### Collections

| Collection | 数据库 | 用途 | 维度 |
|------------|--------|------|------|
| enterprise_knowledge_base | default | 企业知识库 | 1024 |
| industry_knowledge_base | default | 行业知识库 | 1024 |
| macro_knowledge_base | default | 宏观知识库 | 1024 |
| news_semantic_vectors | company_news | 新闻语义向量 | 1024 |
| graph_entities_vectors | company_news | 图谱实体向量 | 1024 |
| graph_relations_vectors | company_news | 图谱关系向量 | 1024 |

### 字段说明

所有 collection 统一字段结构：
- `text` / `source`: 原始文本
- `dense_vector`: 稠密向量 (1024维)
- `sparse_vector`: 稀疏向量 (部分 collection)

### 索引配置

```yaml
index:
  type: HNSW
  params:
    M: 16           # 图连接数
    efConstruction: 200  # 构建时搜索范围
```

## Neo4j 图数据库

```
URI: bolt://localhost:27687
Database: neo4j
```

### 节点类型
- Company: 企业节点
- Person: 人物节点
- Industry: 行业节点

### 关系类型
- INVEST: 投资关系
- EMPLOY: 雇佣关系
- BELONG_TO: 行业归属

## Elasticsearch

```
Host: 192.168.10.156:9200
Scheme: http
```

### 索引
- company_news: 企业新闻
- industry_reports: 行业报告

## Redis

```
Host: redis / localhost
Port: 6379
DB: 1
Max Connections: 200
```

用途：缓存、会话管理、任务队列

## PostgreSQL (主库)

```
URL: postgres:5432/economy_ai_ns
Schema: ai_ns
```

用途：应用数据、用户数据、系统配置
