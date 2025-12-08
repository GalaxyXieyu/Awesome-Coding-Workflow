---
name: data-explorer
description: 数据层探索专家。查询数据、理解结构、优化性能时使用。复用现有方法，避免重复造轮子。只要跟数据服务探索相关的都优先使用这个 skills
tags:
  - data
  - database
  - explore
  - query
  - data-layer
---

# 数据探索专家

探索项目数据层，发现并复用现有查询方法，按规范构建新代码。**复用 > 新建，可执行 > 纸上谈兵**。

## 探索思维

在写代码之前，先回答这些问题：

- **业务目标**: 这个数据用来干什么？谁在用？频率如何？
- **数据定位**: 存在哪个库？什么类型？规模多大？
- **现有资产**: 项目里有没有现成的查询方法？能不能复用？
- **性能约束**: 实时查询（<100ms）还是离线分析（分钟级）？
- **安全边界**: 需要什么权限？数据是否敏感？

**CRITICAL**: 永远先搜索项目现有的查询方法。复用一个成熟的 Repository 方法，比从零写一个"更优雅"的查询更有价值。代码复用 > 代码优雅。

然后生成可直接执行的代码，要求：
- 优先调用项目现有的 Repository/Service/DAO 方法
- 新建方法必须符合项目命名规范和目录结构
- 考虑索引、分页、缓存等性能因素
- 参数化查询，防止注入

**CRITICAL**: 永远先搜索项目现有查询方法。复用成熟的 Repository 方法 > 从零写"更优雅"的查询。

## 能力范围

- **数据库**: PostgreSQL, MySQL, MongoDB, Elasticsearch, Redis, Milvus, Neo4j, InfluxDB
- **优化**: 索引策略、执行计划、N+1诊断、分页、缓存
- **ORM**: SQLAlchemy, Prisma, TypeORM, Sequelize, Django ORM, Mongoose

## 探索流程

### 完整的数据探索 Baseline（7步工程方法）

这个流程是从实战经验中总结出来的端到端方法，适用于所有数据层设计。

```
【输入】业务需求 → 【输出】可投产的数据检索方案 + 性能报告
```

#### 第 1 步：洞察业务需求（需求分解）

**目标**: 明确这个数据查询的真实场景和约束

```
问自己:
□ 用户是谁？什么场景下使用这个数据？
□ 实时响应要求是什么？（秒级/分钟级/小时级）
□ 数据量规模多大？（千/万/百万/亿级）
□ 查询频率如何？（稀疏/常频/高频）
□ 能否缓存？如果能，缓存多久（热度分析）？
□ 是否涉及多个数据源？如果是，数据是否同步？
```

**输出**: 需求清单 + 约束说明

**实战案例**:
```
需求: 获取新闻详情，包括原始 HTML
场景: 编辑审核内容时调用
实时性: <500ms（人类感知阈值）
数据量: 万级新闻
查询频率: 中等（编辑手动查询）
缓存: 可缓存 1 小时（新闻发布后不常变化）
多源: 是，MySQL(权威) + MongoDB(原始HTML)
同步: 未确认，需要验证
```

---

### 第 2 步：可行性分析（数据调研）

**目标**: 确保需求的数据在系统中真的存在且可访问

**CRITICAL**: 这一步决定了后续 5 步是否能成功。跳过这步会导致返工。

```
可行性检查清单:
□ 字段是否存在？（实际有还是假设有？）
□ 字段是否有索引？（查询会全表扫描吗？）
□ 如何查询这个字段？（直接查 vs JOIN vs Aggregation）
□ 数据分布是否正常？（有效数据占比、NULL 率）
□ 跨数据源场景：数据是否有交集？（匹配率多少？）
□ 性能基线：单次查询多久？（无优化状态）
```

**实战子步骤**:

```python
# 步骤 2.1: 字段检查
def check_field_existence():
    """验证字段是否真的存在"""
    doc = mongodb.find_one()
    if "html_content" not in doc:
        raise FieldMissingError("html_content 字段不存在，实际字段: " + list(doc.keys()))

# 步骤 2.2: 索引检查
def check_indexes():
    """检查查询字段是否有索引"""
    indexes = mongodb.index_information()  # 或 mysql.SHOW INDEX FROM table
    if "url_md5" not in str(indexes):
        print("⚠️ url_md5 没有索引，全表扫描会很慢")
        return False
    return True

# 步骤 2.3: 数据分布检查
def analyze_data_distribution():
    """分析数据质量和分布"""
    total = collection.count_documents({})
    valid = collection.count_documents({"html_content": {"$exists": True, "$ne": None}})
    null_rate = (total - valid) / total if total > 0 else 0

    print(f"总文档数: {total}")
    print(f"有效数据: {valid} ({(valid/total)*100:.1f}%)")
    print(f"NULL 率: {null_rate*100:.1f}%")

    if null_rate > 0.3:
        print("⚠️ NULL 率过高，需要处理默认值逻辑")

# 步骤 2.4: 跨源匹配度检查（必做）
def validate_cross_source_match():
    """检查 MySQL 的数据在 MongoDB 中的匹配率"""
    mysql_ids = execute_mysql("SELECT DISTINCT md5_url FROM nanshan_news_label LIMIT 1000")
    mongo_matches = mongodb.find({"url_md5": {"$in": mysql_ids}})
    match_rate = len(mongo_matches) / len(mysql_ids)

    if match_rate < 0.3:
        raise DataMismatchError(f"匹配率仅 {match_rate:.1%}，不可继续")

    return mongo_matches[:5]  # 返回测试用 ID

# 步骤 2.5: 性能基线（无任何优化）
def measure_baseline_performance():
    """单次查询的原始性能"""
    import time
    test_ids = ["xxx", "yyy", "zzz"]  # 从步骤 2.4 获得

    times = []
    for test_id in test_ids:
        start = time.time()
        result = mongodb.find_one({"url_md5": test_id})
        times.append(time.time() - start)

    avg_time = sum(times) / len(times)
    print(f"单次查询耗时: {avg_time*1000:.2f}ms")

    # 判断是否需要优化
    if avg_time > 0.1:  # 100ms
        print("⚠️ 性能基线超过 100ms，需要优化")
```

**输出**: 可行性报告 + 可用测试数据 + 性能基线数据

---

### 第 3 步：构建测试样例（数据固定化）

**目标**: 有一套可复现的测试数据，贯穿整个开发 → 测试 → 性能评估流程

```python
class TestDataRegistry:
    """测试数据注册表 - 确保整个流程用的是同一批数据"""

    # 必须来自步骤 2.4 的可行性分析
    TEST_IDS = [
        "dc0a8cdd8d4ac05f7a7443ab62816ae0",  # MySQL + MongoDB 都有
        "fd782ef7db31731a8e3d11b4d8d2e96f",  # 两边都有
        "ba1967bf0393af71dc410c68c2e3450f",  # 两边都有
    ]

    # 期望结果（从步骤 2 中获取的真实数据）
    EXPECTED_RESULTS = {
        "dc0a8cdd8d4ac05f7a7443ab62816ae0": {
            "title": "2025清华\"科创杯\"创业大赛...",
            "html_content_length": 45000,  # 或者 None（如果 MongoDB 没有）
            "content": "处理后的文本内容...",
        },
        # ... 更多测试用例
    }

    @staticmethod
    def validate_test_setup():
        """确保测试数据有效"""
        for test_id in TestDataRegistry.TEST_IDS:
            # 验证这个 ID 在 MySQL 中存在
            mysql_result = query_mysql(f"SELECT * FROM nanshan_news_label WHERE md5_url = '{test_id}'")
            assert mysql_result is not None, f"测试 ID {test_id} 在 MySQL 中不存在"

            # 验证这个 ID 在 MongoDB 中存在（如果需要）
            mongo_result = query_mongo({"url_md5": test_id})
            assert mongo_result is not None, f"测试 ID {test_id} 在 MongoDB 中不存在"
```

**输出**: 固定的测试数据集 + 期望结果

---

### 第 4 步：构建高性能检索方案（架构设计）

**目标**: 设计一个满足性能约束、避免影响业务的查询方案

```
性能方案设计清单:
□ 数据库选择：PostgreSQL/MySQL/MongoDB 哪个作为主查询源？
□ 索引策略：需要新建哪些索引？复合索引如何设计？
□ 分页策略：用 limit/offset 还是 cursor？
□ 缓存策略：Redis/内存 缓存多少数据？TTL 多久？
□ 异步处理：需要 MQ 异步化吗？还是同步查询足够？
□ 熔断限制：单次查询最大文档数/响应大小？
□ 监控告警：哪些指标需要告警？阈值多少？
```

**实战案例**:

```python
class NewsDetailQueryPlan:
    """新闻详情查询方案"""

    # 性能约束
    SLA_RESPONSE_TIME = 500  # ms
    MAX_FETCH_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_TIMEOUT = 3000  # ms

    async def get_news_detail(self, md5_url: str):
        """
        高性能检索方案：
        1. 先查 Redis 缓存 (TTL: 1小时)
        2. 缓存未命中 → 查 MySQL 主表
        3. MySQL 找到 → 异步补充 MongoDB 原始 HTML
        4. 构造响应，返回

        性能目标: <500ms (P95)
        """

        # 步骤 1: 缓存检查（快路径）
        cache_key = f"news:detail:{md5_url}"
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)  # 缓存命中，直接返回

        # 步骤 2: MySQL 查询（主路径）
        mysql_result = await mysql.query(
            "SELECT * FROM nanshan_news_label WHERE md5_url = %s",
            (md5_url,),
            timeout=100  # 100ms 超时
        )

        if not mysql_result:
            raise HTTPException(status_code=404)

        result = dict(mysql_result)

        # 步骤 3: MongoDB 异步补充（非关键路径）
        mongo_html = await asyncio.wait_for(
            self._get_mongo_html(md5_url),
            timeout=200  # 200ms 超时，超时也不影响返回
        )

        if mongo_html:
            result["html_content"] = mongo_html
            result["content_source"] = "raw_html"
        else:
            result["content_source"] = "database"

        # 步骤 4: 缓存结果
        await redis.setex(
            cache_key,
            3600,  # 1 小时过期
            json.dumps(result)
        )

        return result

    async def _get_mongo_html(self, md5_url: str):
        """从 MongoDB 获取原始 HTML，超时时不报错"""
        try:
            doc = await mongodb.find_one({"url_md5": md5_url})
            return doc.get("html_content") if doc else None
        except Exception as e:
            logger.warning(f"MongoDB 查询失败: {e}")
            return None  # 降级处理
```

**输出**: 完整的查询架构设计 + 性能目标

---

### 第 5 步：实现查询函数 + 测试验证（编码 + 调试）

**目标**: 用第 3 步的测试数据验证实现的正确性

```python
async def test_news_detail_retrieval():
    """用测试数据进行完整验证"""

    for test_id in TestDataRegistry.TEST_IDS:
        # 执行查询
        result = await news_service.get_news_detail(test_id)

        # 验证返回数据
        assert result is not None, f"ID {test_id} 返回为空"
        assert result["md5_url"] == test_id, "返回数据不匹配"
        assert result["title"], "标题缺失"
        assert "content_source" in result, "content_source 字段缺失"

        # 验证业务逻辑
        if result["content_source"] == "raw_html":
            assert result.get("html_content"), "html_content 应该有值"
            assert len(result["html_content"]) > 100, "html_content 太短"

        print(f"✅ 测试用例 {test_id} 通过")

    print("✅ 所有测试用例通过")
```

**输出**: 通过所有测试用例的可用代码

---

### 第 6 步：效率评估（性能测试）

**目标**: 在实际约束下评估查询性能是否达到 SLA

```python
async def benchmark_query_performance():
    """完整的性能评估"""

    import statistics

    # 配置
    WARMUP_RUNS = 10        # 预热
    BENCHMARK_RUNS = 100    # 基准测试
    CONCURRENT_USERS = 10   # 并发模拟

    print("=" * 80)
    print("性能基准测试")
    print("=" * 80)

    # 步骤 1: 缓存预热
    print("\n[1/4] 缓存预热...")
    for test_id in TestDataRegistry.TEST_IDS * 5:
        await news_service.get_news_detail(test_id)

    # 步骤 2: 单线程性能
    print("[2/4] 单线程性能测试...")
    response_times = []
    for test_id in TestDataRegistry.TEST_IDS * (BENCHMARK_RUNS // len(TestDataRegistry.TEST_IDS)):
        start = time.time()
        result = await news_service.get_news_detail(test_id)
        elapsed = (time.time() - start) * 1000  # 转为 ms
        response_times.append(elapsed)

    # 步骤 3: 统计指标
    print("[3/4] 性能统计...")
    stats = {
        "count": len(response_times),
        "min": min(response_times),
        "max": max(response_times),
        "avg": statistics.mean(response_times),
        "median": statistics.median(response_times),
        "p95": sorted(response_times)[int(len(response_times) * 0.95)],
        "p99": sorted(response_times)[int(len(response_times) * 0.99)],
    }

    print("\n查询性能指标:")
    print(f"  最小: {stats['min']:.2f}ms")
    print(f"  平均: {stats['avg']:.2f}ms")
    print(f"  中位: {stats['median']:.2f}ms")
    print(f"  P95:  {stats['p95']:.2f}ms")
    print(f"  P99:  {stats['p99']:.2f}ms")
    print(f"  最大: {stats['max']:.2f}ms")

    # 步骤 4: 性能评估
    print("[4/4] 性能评估...")
    SLA_TARGET = 500  # ms

    if stats["p95"] < SLA_TARGET:
        print(f"✅ 性能达标: P95 {stats['p95']:.2f}ms < {SLA_TARGET}ms")
    else:
        print(f"❌ 性能未达标: P95 {stats['p95']:.2f}ms > {SLA_TARGET}ms")
        print("   建议: 增加缓存/添加索引/数据分片")

    # 步骤 5: 并发测试
    print("\n[并发压力测试]")
    async def concurrent_test():
        tasks = []
        for i in range(CONCURRENT_USERS * 10):
            test_id = TestDataRegistry.TEST_IDS[i % len(TestDataRegistry.TEST_IDS)]
            tasks.append(news_service.get_news_detail(test_id))

        start = time.time()
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start

        throughput = len(results) / elapsed
        print(f"  并发用户: {CONCURRENT_USERS}")
        print(f"  吞吐量: {throughput:.2f} req/s")
        print(f"  总耗时: {elapsed:.2f}s")

    await concurrent_test()

    return stats
```

**输出**: 详细的性能报告 + 瓶颈分析

---

### 第 7 步：生成最终报告（交付文档）

**目标**: 清晰地记录整个方案，便于后续维护和审计

```markdown
# 新闻详情数据检索方案报告

## 📋 背景说明

**业务需求**: 编辑在审核页面查看新闻详情，包括原始 HTML
**响应时间要求**: <500ms (P95)
**年查询量**: ~100万次（月均）

## 📊 涉及的数据源

| 数据源 | 表/集合 | 字段 | 用途 | 数据量 |
|-------|--------|------|------|--------|
| MySQL | nanshan_ent_qxb.nanshan_news_label | md5_url, title, content | 权威数据 | 50万 |
| MongoDB | WaiQian_JingYing_FuChi.new_09_detail | url_md5, html_content | 原始 HTML | 87万 |

**数据匹配度**: 35万条 (70%)

## 🏗️ 代码架构

```
src/
├── domain/services/
│   └── news_detail_service.py      # 业务逻辑层（缓存+查询组合）
├── infrastructure/
│   ├── repositories/
│   │   ├── mysql_news_repo.py      # MySQL 查询
│   │   └── mongo_html_repo.py      # MongoDB 查询
│   └── cache/
│       └── news_cache.py           # Redis 缓存层
└── presentation/api/
    └── endpoints/news.py           # API 端点
```

## 📈 性能指标

**单线程性能** (100 次查询):
- 平均: 45ms
- P95: 120ms ✅ (达到 SLA 500ms)
- P99: 280ms

**并发压力** (10 用户 × 10 请求):
- 吞吐量: 220 req/s
- 无错误率

**缓存效果**:
- 命中率: 75% (生产预期)
- 缓存加速: 8-10x

## ⚡ 优化措施

1. **Redis 缓存** - TTL 1小时，预期命中率 75%
2. **复合索引** - MongoDB 的 url_md5 + html_content
3. **异步补充** - MongoDB 查询不阻塞主响应
4. **熔断限制** - 200ms 超时，MongoDB 不可用时降级

## ✅ 验证清单

- [x] MySQL 数据库可访问
- [x] MongoDB 数据库可访问
- [x] 数据匹配率达到 70%
- [x] 所有测试用例通过
- [x] 性能达到 SLA
- [x] 缓存策略有效
- [x] 异常处理完善

## 🚀 部署建议

1. 提前预热 Redis 缓存（导入热数据）
2. 监控 MongoDB 连接状态，及时告警
3. 设置 P95 响应时间告警阈值为 300ms
4. 周期性回源验证缓存数据新鲜度

---

生成时间: 2025-12-03
验证者: AI Data Explorer
```

**输出**: 可投产的完整报告

---


### 0. 跨数据源集成预检（当涉及多个数据源时必做）⚠️

**CRITICAL**: 多数据源集成容易导致返工，务必在编码前做完整预检。

### 第 1 层：理解业务需求

```
问自己:
□ 用户要获取什么字段/数据?
□ 这些数据用来做什么?
□ 需要什么维度的数据聚合?
□ 是否涉及多个数据源/表? → 如果是，先做"步骤 0"预检
□ 实时性要求 vs 计算成本?
```

**输出**: 业务需求分解文档


### 2. 探索数据源
```bash
# 找配置
grep -r "DATABASE_URL\|DB_HOST\|MONGO_URI" . --include="*.env*" --include="*.yml" 2>/dev/null
# 找 schema
find . -name "*database*" -o -name "*schema*" -o -name "*migration*" | head -20
# 识别驱动
grep -E "postgres|mongodb|mysql|elasticsearch" package.json requirements.txt 2>/dev/null
```

### 3. 发现现有方法（核心）
```bash
# 找 Repository/DAO/Service
find . -type f \( -name "*Repository*" -o -name "*Dao*" -o -name "*Service*" \) ! -path "*/node_modules/*" | head -20
# 找查询方法
grep -r "def get_\|def find_\|def list_" . --include="*.py" | head -20
grep -r "findOne\|findAll\|findBy" . --include="*.ts" --include="*.js" | head -20
```

**决策**: 有现成 → 直接用 | 有类似 → 扩展参数 | 没有 → 按规范新建

### 4. 识别字段类型（增删改查前必做）

**CRITICAL**: 在写任何数据操作代码前，必须先识别字段管理策略。

#### 字段分类侦探工作
```bash
# 1. 找 Model/Entity 定义
find . -type f \( -name "*model*" -o -name "*entity*" -o -name "*schema*" \) \
  ! -path "*/node_modules/*" ! -path "*/venv/*" | head -20

# 2. 找 Migration 文件（最可靠）
find . -name "*migration*" -o -name "*alembic*" -o -name "*prisma*" | head -10

# 3. 检查表结构（直连数据库时）
# PostgreSQL: \d+ table_name
# MySQL: SHOW CREATE TABLE table_name;
```

#### 字段类型识别清单
```
自动管理字段（框架/数据库生成，不能手动赋值）:
□ id (主键): AUTO_INCREMENT / SERIAL / @default(autoincrement())
□ created_at: DEFAULT CURRENT_TIMESTAMP / @default(now())
□ updated_at: ON UPDATE CURRENT_TIMESTAMP / @updatedAt
□ uuid: @default(uuid()) / DEFAULT gen_random_uuid()
□ version: 乐观锁版本号（ORM自动管理）

手动赋值字段（业务逻辑计算/用户输入）:
□ user_id: 外键，从上下文获取
□ status: 业务状态，显式指定
□ name/email: 用户输入
□ computed_field: 业务计算字段

条件管理字段（看场景）:
□ deleted_at: 软删除，由删除操作赋值
□ last_login_at: 由登录逻辑更新
```

#### 实战示例：创建用户

**❌ 错误示例**（混淆自动/手动字段）:
```python
# 坏示例：手动赋值自动生成字段
user = User(
    id=123,  # ❌ 数据库自动生成，不应手动赋值
    name="Alice",
    email="alice@example.com",
    created_at=datetime.now(),  # ❌ DEFAULT CURRENT_TIMESTAMP 已设置
    updated_at=datetime.now()   # ❌ 触发器/ORM自动管理
)
```

**✅ 正确示例**（只赋值手动字段）:
```python
# 好示例：只传必需的手动字段
user = User(
    name="Alice",          # ✅ 手动赋值
    email="alice@example.com",  # ✅ 手动赋值
    status="active",       # ✅ 业务字段
    role_id=3             # ✅ 外键，从上下文获取
)
# id, created_at, updated_at 由数据库/ORM自动生成
session.add(user)
session.commit()
```

#### 验证方法
```python
# 方法1：检查 Model 定义
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)  # 🤖 自动
    created_at = Column(DateTime, server_default=func.now())    # 🤖 自动
    updated_at = Column(DateTime, onupdate=func.now())          # 🤖 自动
    name = Column(String(100), nullable=False)                  # ✋ 手动
    email = Column(String(255), unique=True)                    # ✋ 手动

# 方法2：测试插入空对象
user = User()  # 看哪些字段报错 = 必须手动赋值
```

### 5. 规范化新建（无现成时）

**目录结构**: `models/`(表结构) → `repositories/`(单表操作) → `services/`(业务组合) → `schemas/`(DTO)

**命名规范**: `get_by_{field}` | `list_{entities}` | `find_by_{condition}` | `create/update/delete_{entity}`

**Repository 模板**（带字段识别注释）:
```python
class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: int) -> User | None:
        """查询：不涉及字段生成"""
        return self.session.query(User).filter(User.id == user_id).first()

    def create(self, name: str, email: str, role_id: int) -> User:
        """创建：只传手动字段，id/created_at自动生成"""
        user = User(
            name=name,        # ✋ 手动
            email=email,      # ✋ 手动
            role_id=role_id   # ✋ 手动（外键）
            # id, created_at, updated_at 自动生成 🤖
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)  # 获取自动生成的值
        return user

    def update(self, user_id: int, **kwargs) -> User:
        """更新：updated_at 自动更新"""
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # 只更新手动字段
        allowed_fields = {'name', 'email', 'status'}  # 白名单
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(user, key, value)

        # updated_at 由 onupdate 自动处理 🤖
        self.session.commit()
        self.session.refresh(user)
        return user

    def list_by_status(self, status: str, limit: int = 100, offset: int = 0) -> list[User]:
        """查询：分页标配"""
        return self.session.query(User)\
            .filter(User.status == status)\
            .order_by(User.created_at.desc())\
            .limit(limit).offset(offset).all()
```

**原则**:
- 单一职责（一个 Repository 一张表）
- **字段白名单**（明确区分自动/手动字段）
- 参数化（避免硬编码）
- 分页标配
- Service 层控制事务

### 5. 查询优化
| 数据库 | 推荐 | 避免 |
|-------|-----|------|
| PostgreSQL/MySQL | 参数化SQL + 索引 | 字符串拼接、SELECT * |
| MongoDB | Aggregation Pipeline | 客户端循环处理 |
| Elasticsearch | Query DSL | 全表扫描后过滤 |

**性能检查**: 用索引了吗 → N+1问题 → 分页了吗 → 需要缓存吗

### 6. 验证
结果正确？性能达标？需要缓存？日志正常？

## 元数据沉淀
发现的 schema 存到 `references/schema/`，查询方法记录到 `references/queries/existing_queries.yaml`

## NEVER
- 不预设数据库类型，先探索再决策
- 不跳过现有方法搜索
- 不执行 DELETE/DROP 不确认
- 不忽视分页
- 不硬编码连接信息
- **不跳过跨数据源预检（会导致多次返工）**
- **不用单一数据源的测试数据测试集成功能（会出现虚假成功）**

---

## 常见坑与避坑指南

### 坑 #1: 跨数据源集成未做数据匹配验证

**症状**: 代码写好了，测试一直 404 或者返回空数据

**根因**: 没有验证两个数据源的关联键是否有实际交集

**避坑**:
```python
# 在写代码前，先运行这个验证脚本
def validate_before_coding():
    # 1. 获取主数据源的 100 个 ID
    mysql_ids = get_mysql_sample_ids(100)

    # 2. 在 MongoDB 中查找这些 ID
    mongo_matches = mongodb.find({"url_md5": {"$in": mysql_ids}})

    # 3. 计算匹配率
    match_rate = len(mongo_matches) / len(mysql_ids)

    if match_rate < 0.3:
        print(f"❌ 数据匹配率仅 {match_rate:.1%}，不建议继续")
        print("建议: 检查数据同步、字段映射、数据时间范围")
        return False

    print(f"✅ 数据匹配率: {match_rate:.1%}")
    print(f"可用测试 ID: {mongo_matches[:5]}")
    return True
```

### 坑 #2: Settings 配置不完整导致运行时错误

**症状**: 代码语法正确，但运行时报 `AttributeError: 'Settings' object has no attribute 'XXX'`

**根因**: 在 `.env` 中添加了配置，但忘记在 `settings.py` 的 Settings 类中添加对应字段

**避坑检查清单**:
```
□ 在 .env 中添加了配置变量
□ 在 settings.py 的 Settings 类中添加了对应的 Field 定义
□ 重启了应用（Settings 是启动时加载的）
□ 用 settings.FIELD_NAME 测试是否能访问
```

### 坑 #3: 字段名假设错误

**症状**: MongoDB 查询返回空，但数据明明存在

**根因**: 假设字段名是 `md5_url`，实际是 `url_md5`

**避坑**:
```python
# 永远先查看实际数据结构
def inspect_first_document(collection):
    doc = collection.find_one()
    if doc:
        print("实际字段:", list(doc.keys()))
        for key, value in doc.items():
            print(f"  {key}: {type(value).__name__}")
    return doc
```

### 坑 #4: 测试数据选择错误

**症状**: 单独测试 MongoDB 和 MySQL 都成功，但集成测试 404

**根因**: 用的测试 ID 只在一个数据源中存在

**避坑**:
```python
# 必须用两边都存在的 ID 测试
test_ids = get_ids_exist_in_both_sources()
```

---

**IMPORTANT**: 一个被复用100次的 Repository 方法，比100个一次性查询更有价值。
**CRITICAL**: 跨数据源集成必须先做数据匹配验证，否则会浪费大量时间在调试不存在的问题上。
