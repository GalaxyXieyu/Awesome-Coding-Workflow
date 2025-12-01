#!/usr/bin/env python3
"""
Neo4j 图数据库查询脚本

用途：执行 Cypher 查询获取图谱数据
调用：python query_neo4j.py "<cypher_query>" [--limit 100]
输出：JSON 格式的查询结果
"""
import sys
import json
import argparse
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))


def log_error(msg: str):
    sys.stderr.write(f"ERROR: {msg}\n")


def log_info(msg: str):
    sys.stderr.write(f"INFO: {msg}\n")


# 预设查询模板
QUERY_TEMPLATES = {
    "company_relations": """
        MATCH (c:Company {name: $company_name})-[r]->(related)
        RETURN c.name as source, type(r) as relation, labels(related)[0] as target_type, related.name as target
        LIMIT $limit
    """,
    "investment_chain": """
        MATCH path = (c:Company {name: $company_name})-[:INVEST*1..3]->(invested)
        RETURN path
        LIMIT $limit
    """,
    "common_investors": """
        MATCH (c1:Company {name: $company1})<-[:INVEST]-(investor)-[:INVEST]->(c2:Company {name: $company2})
        RETURN investor.name as common_investor
        LIMIT $limit
    """
}


def parse_args():
    parser = argparse.ArgumentParser(description="Neo4j 查询")
    parser.add_argument("query", help="Cypher 查询语句或模板名称")
    parser.add_argument("--limit", type=int, default=100, help="结果限制")
    parser.add_argument("--params", type=str, default="{}", help="查询参数 (JSON 格式)")
    return parser.parse_args()


def get_neo4j_driver():
    """获取 Neo4j 连接"""
    try:
        from neo4j import GraphDatabase
        from dotenv import load_dotenv
        
        env_path = PROJECT_ROOT / "backend/.env"
        load_dotenv(env_path)
        
        uri = os.getenv("NEO4J_URI", "bolt://localhost:27687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "")
        
        return GraphDatabase.driver(uri, auth=(username, password))
    except Exception as e:
        log_error(f"Neo4j 连接失败: {e}")
        return None


def execute_query(query: str, params: dict, limit: int) -> dict:
    """执行 Cypher 查询"""
    driver = get_neo4j_driver()
    if not driver:
        return {"error": "Neo4j 连接失败"}
    
    try:
        # 检查是否是模板查询
        if query in QUERY_TEMPLATES:
            cypher = QUERY_TEMPLATES[query]
        else:
            cypher = query
        
        params['limit'] = limit
        
        with driver.session() as session:
            result = session.run(cypher, params)
            records = []
            for record in result:
                records.append(dict(record))
            
            return {
                "query": query,
                "params": params,
                "count": len(records),
                "data": records
            }
    except Exception as e:
        return {"error": str(e)}
    finally:
        driver.close()


def main():
    args = parse_args()
    log_info(f"执行查询: {args.query[:50]}...")
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError:
        log_error("params 必须是有效的 JSON")
        sys.exit(1)
    
    result = execute_query(args.query, params, args.limit)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    
    if "error" in result:
        sys.exit(1)


if __name__ == '__main__':
    main()
