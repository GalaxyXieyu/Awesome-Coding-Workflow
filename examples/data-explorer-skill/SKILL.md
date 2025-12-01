---
name: data-explorer
description: 探索项目数据层，发现数据库、查询工具、schema，并缓存元数据
---

# 数据探索专家

## 触发场景

用户说"我要查xxx数据"并告诉你项目路径

## 探索流程

### 1. 理解业务
- 用户要什么数据？
- 用来做什么？

### 2. 探索数据源
用 grep/find 自己搜，根据需求决定关键词：
- 配置文件在哪？(.env, config, settings)
- 什么类型的数据库？
- 连接方式是什么？

### 3. 探索现有工具
项目里有没有封装好的查询方法？
- **有就用现成的**
- **没有再自己写**

### 4. 提取 Schema（可选）
如果需要了解表结构，用 `scripts/extract_schema.py` 连接数据库提取：
```bash
python scripts/extract_schema.py -t <pg|mysql|dm|neo4j|milvus|es> -H <host> -d <db> -u <user> -o ./references/schema/
```

### 5. 执行查询
优先用项目已有的方法调用

### 6. 验证
- 结果对不对？
- 原来实现有没有漏洞？

## 核心原则

- **不预设**：根据实际需求决定怎么探索
- **复用优先**：项目有工具就用，没有再写
- **元数据沉淀**：发现的 schema 存到 references/schema/
