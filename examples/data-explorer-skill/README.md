# 数据探索 Skill

**动态探索**项目数据层，而不是预设查询。

## 核心思路

```
用户输入: 业务需求 + 项目路径
          │
          ▼
    ┌─────────────────────────────────────┐
    │         探索循环                      │
    │  1. 业务是什么？                      │
    │  2. 数据库在哪？                      │
    │  3. 什么字段跟业务有关？              │
    │  4. 有封装好的查询工具吗？            │
    │  5. 怎么调用？                        │
    │  6. 验证结果                          │
    └─────────────────────────────────────┘
          │
          ▼
    输出: 探索报告 + 查询结果 + 元数据缓存
```

## 目录结构

```
data-explorer-skill/
├── SKILL.md                    # 探索流程定义
├── scripts/                    # 探索工具
│   ├── find_datasources.sh     # 发现数据源配置
│   ├── find_schemas.sh         # 发现数据模型
│   ├── find_query_tools.sh     # 发现现有查询工具
│   └── extract_schema.py       # 提取 schema 元数据
└── references/
    └── schema/                 # 动态生成的 schema 缓存
```

## 使用流程

### 1. 探索数据源

```bash
./scripts/find_datasources.sh /path/to/project
```

### 2. 探索数据模型

```bash
./scripts/find_schemas.sh /path/to/project
```

### 3. 探索查询工具

```bash
./scripts/find_query_tools.sh /path/to/project
```

### 4. 提取 Schema 元数据

```bash
python scripts/extract_schema.py /path/to/project ./references/schema/
```

## 与预设查询的区别

| 预设查询 Skill | 动态探索 Skill |
|---------------|---------------|
| 写死数据库配置 | 探索发现配置 |
| 预设查询脚本 | 先找现有工具 |
| 固定 schema | 动态提取缓存 |
| 单一项目适用 | 任意项目适用 |

## 元数据沉淀

探索发现的 schema 会保存到 `references/schema/`，下次再查同一项目时可以直接使用。
