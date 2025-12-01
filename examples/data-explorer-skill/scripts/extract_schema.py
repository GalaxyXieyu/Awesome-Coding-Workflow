#!/usr/bin/env python3
"""
从数据库直接提取 Schema 元数据

支持: PostgreSQL, MySQL, 达梦(DM), Neo4j, Milvus, Elasticsearch

用法: 
  python extract_schema.py --type pg --host localhost --port 5432 --db mydb --user user --output ./schema/
  python extract_schema.py --type mysql --host localhost --port 3306 --db mydb --user user --output ./schema/
  python extract_schema.py --type dm --host localhost --port 5236 --db mydb --user user --output ./schema/
  python extract_schema.py --type neo4j --host localhost --port 7687 --user neo4j --output ./schema/
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime


def extract_pg_schema(host, port, db, user, password, schema='public'):
    """PostgreSQL schema 提取"""
    try:
        import psycopg2
        conn = psycopg2.connect(host=host, port=port, database=db, user=user, password=password)
        cur = conn.cursor()
        
        # 获取所有表
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
        """, (schema,))
        tables = [row[0] for row in cur.fetchall()]
        
        result = {'type': 'postgresql', 'database': db, 'schema': schema, 'tables': {}}
        
        for table in tables:
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
            """, (schema, table))
            columns = [{'name': r[0], 'type': r[1], 'nullable': r[2], 'default': r[3]} for r in cur.fetchall()]
            result['tables'][table] = {'columns': columns}
        
        conn.close()
        return result
    except Exception as e:
        return {'error': str(e)}


def extract_mysql_schema(host, port, db, user, password):
    """MySQL schema 提取"""
    try:
        import pymysql
        conn = pymysql.connect(host=host, port=int(port), database=db, user=user, password=password)
        cur = conn.cursor()
        
        cur.execute("SHOW TABLES")
        tables = [row[0] for row in cur.fetchall()]
        
        result = {'type': 'mysql', 'database': db, 'tables': {}}
        
        for table in tables:
            cur.execute(f"DESCRIBE `{table}`")
            columns = [{'name': r[0], 'type': r[1], 'nullable': r[2], 'key': r[3], 'default': r[4]} for r in cur.fetchall()]
            result['tables'][table] = {'columns': columns}
        
        conn.close()
        return result
    except Exception as e:
        return {'error': str(e)}


def extract_dm_schema(host, port, db, user, password, schema=None):
    """达梦数据库 schema 提取"""
    try:
        import dmPython
        conn = dmPython.connect(host=host, port=int(port), user=user, password=password)
        cur = conn.cursor()
        
        schema = schema or user.upper()
        
        # 获取所有表
        cur.execute(f"""
            SELECT TABLE_NAME FROM DBA_TABLES WHERE OWNER = '{schema}'
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        result = {'type': 'dameng', 'database': db, 'schema': schema, 'tables': {}}
        
        for table in tables:
            cur.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE, NULLABLE, DATA_DEFAULT
                FROM DBA_TAB_COLUMNS 
                WHERE OWNER = '{schema}' AND TABLE_NAME = '{table}'
                ORDER BY COLUMN_ID
            """)
            columns = [{'name': r[0], 'type': r[1], 'nullable': r[2], 'default': r[3]} for r in cur.fetchall()]
            result['tables'][table] = {'columns': columns}
        
        conn.close()
        return result
    except ImportError:
        return {'error': '需要安装 dmPython: pip install dmPython'}
    except Exception as e:
        return {'error': str(e)}


def extract_neo4j_schema(host, port, user, password):
    """Neo4j schema 提取（节点标签和关系类型）"""
    try:
        from neo4j import GraphDatabase
        uri = f"bolt://{host}:{port}"
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        result = {'type': 'neo4j', 'labels': [], 'relationships': [], 'properties': {}}
        
        with driver.session() as session:
            # 获取所有标签
            labels = session.run("CALL db.labels()").data()
            result['labels'] = [l['label'] for l in labels]
            
            # 获取所有关系类型
            rels = session.run("CALL db.relationshipTypes()").data()
            result['relationships'] = [r['relationshipType'] for r in rels]
            
            # 获取属性 keys
            props = session.run("CALL db.propertyKeys()").data()
            result['property_keys'] = [p['propertyKey'] for p in props]
        
        driver.close()
        return result
    except Exception as e:
        return {'error': str(e)}


def extract_milvus_schema(host, port):
    """Milvus collection schema 提取"""
    try:
        from pymilvus import connections, utility, Collection
        connections.connect(host=host, port=port)
        
        collections = utility.list_collections()
        result = {'type': 'milvus', 'collections': {}}
        
        for coll_name in collections:
            coll = Collection(coll_name)
            schema = coll.schema
            fields = [{'name': f.name, 'type': str(f.dtype), 'dim': getattr(f, 'dim', None)} for f in schema.fields]
            result['collections'][coll_name] = {'fields': fields, 'description': schema.description}
        
        connections.disconnect("default")
        return result
    except Exception as e:
        return {'error': str(e)}


def extract_es_schema(host, port, user=None, password=None):
    """Elasticsearch index mapping 提取"""
    try:
        from elasticsearch import Elasticsearch
        if user and password:
            es = Elasticsearch([f"http://{host}:{port}"], basic_auth=(user, password))
        else:
            es = Elasticsearch([f"http://{host}:{port}"])
        
        indices = es.indices.get_alias(index="*")
        result = {'type': 'elasticsearch', 'indices': {}}
        
        for index_name in indices.keys():
            if not index_name.startswith('.'):
                mapping = es.indices.get_mapping(index=index_name)
                result['indices'][index_name] = mapping[index_name]['mappings']
        
        return result
    except Exception as e:
        return {'error': str(e)}


def generate_markdown(schema_data: dict, output_path: Path):
    """生成 Markdown 格式的 schema 文档"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    db_type = schema_data.get('type', 'unknown')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {db_type.upper()} Schema\n\n")
        f.write(f"提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if 'error' in schema_data:
            f.write(f"**错误**: {schema_data['error']}\n")
            return
        
        if db_type in ('postgresql', 'mysql', 'dameng'):
            f.write(f"数据库: `{schema_data.get('database', 'N/A')}`\n\n")
            for table, info in schema_data.get('tables', {}).items():
                f.write(f"## {table}\n\n")
                f.write("| 字段 | 类型 | 可空 | 默认值 |\n")
                f.write("|------|------|------|--------|\n")
                for col in info['columns']:
                    f.write(f"| {col['name']} | {col['type']} | {col.get('nullable', '')} | {col.get('default', '')} |\n")
                f.write("\n")
        
        elif db_type == 'neo4j':
            f.write("## 节点标签\n\n")
            for label in schema_data.get('labels', []):
                f.write(f"- `:{label}`\n")
            f.write("\n## 关系类型\n\n")
            for rel in schema_data.get('relationships', []):
                f.write(f"- `[:{rel}]`\n")
            f.write("\n## 属性 Keys\n\n")
            for prop in schema_data.get('property_keys', []):
                f.write(f"- `{prop}`\n")
        
        elif db_type == 'milvus':
            for coll, info in schema_data.get('collections', {}).items():
                f.write(f"## {coll}\n\n")
                f.write(f"描述: {info.get('description', 'N/A')}\n\n")
                f.write("| 字段 | 类型 | 维度 |\n")
                f.write("|------|------|------|\n")
                for field in info['fields']:
                    f.write(f"| {field['name']} | {field['type']} | {field.get('dim', '-')} |\n")
                f.write("\n")
        
        elif db_type == 'elasticsearch':
            for index, mapping in schema_data.get('indices', {}).items():
                f.write(f"## {index}\n\n")
                f.write("```json\n")
                f.write(json.dumps(mapping, indent=2, ensure_ascii=False))
                f.write("\n```\n\n")


def main():
    parser = argparse.ArgumentParser(description="数据库 Schema 提取工具")
    parser.add_argument("--type", "-t", required=True, choices=['pg', 'mysql', 'dm', 'neo4j', 'milvus', 'es'], help="数据库类型")
    parser.add_argument("--host", "-H", default="localhost", help="主机地址")
    parser.add_argument("--port", "-p", type=int, help="端口")
    parser.add_argument("--db", "-d", help="数据库名")
    parser.add_argument("--user", "-u", help="用户名")
    parser.add_argument("--password", "-P", default="", help="密码")
    parser.add_argument("--schema", "-s", help="Schema 名 (PG/DM)")
    parser.add_argument("--output", "-o", default="./schema", help="输出目录")
    
    args = parser.parse_args()
    
    # 默认端口
    default_ports = {'pg': 5432, 'mysql': 3306, 'dm': 5236, 'neo4j': 7687, 'milvus': 19530, 'es': 9200}
    port = args.port or default_ports.get(args.type)
    
    print(f"=== 提取 {args.type.upper()} Schema ===")
    print(f"连接: {args.host}:{port}")
    
    # 提取 schema
    if args.type == 'pg':
        schema_data = extract_pg_schema(args.host, port, args.db, args.user, args.password, args.schema or 'public')
    elif args.type == 'mysql':
        schema_data = extract_mysql_schema(args.host, port, args.db, args.user, args.password)
    elif args.type == 'dm':
        schema_data = extract_dm_schema(args.host, port, args.db, args.user, args.password, args.schema)
    elif args.type == 'neo4j':
        schema_data = extract_neo4j_schema(args.host, port, args.user, args.password)
    elif args.type == 'milvus':
        schema_data = extract_milvus_schema(args.host, port)
    elif args.type == 'es':
        schema_data = extract_es_schema(args.host, port, args.user, args.password)
    
    # 输出
    output_dir = Path(args.output)
    output_file = output_dir / f"{args.type}_schema.md"
    
    generate_markdown(schema_data, output_file)
    print(f"输出: {output_file}")
    
    # 同时输出 JSON
    json_file = output_dir / f"{args.type}_schema.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(schema_data, f, indent=2, ensure_ascii=False, default=str)
    print(f"JSON: {json_file}")
    
    if 'error' in schema_data:
        print(f"错误: {schema_data['error']}")
        sys.exit(1)
    
    print("=== 完成 ===")


if __name__ == '__main__':
    main()
