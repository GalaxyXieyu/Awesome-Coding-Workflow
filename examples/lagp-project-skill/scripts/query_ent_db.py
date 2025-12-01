#!/usr/bin/env python3
"""
企业数据库查询脚本

用途：查询企业工商信息
调用：python query_ent_db.py <company_name> [--fields "field1,field2"]
输出：JSON 格式的企业信息
"""
import sys
import json
import argparse
import os
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))


def log_error(msg: str):
    sys.stderr.write(f"ERROR: {msg}\n")


def log_info(msg: str):
    sys.stderr.write(f"INFO: {msg}\n")


def parse_args():
    parser = argparse.ArgumentParser(description="查询企业数据库")
    parser.add_argument("company_name", help="企业名称（支持模糊匹配）")
    parser.add_argument("--fields", default="*", help="返回字段，逗号分隔")
    parser.add_argument("--limit", type=int, default=10, help="返回条数限制")
    return parser.parse_args()


def get_db_connection():
    """获取数据库连接（从 datasources.yaml 读取配置）"""
    try:
        import yaml
        import pymysql
        
        config_path = PROJECT_ROOT / "backend/src/infrastructure/config/datasources.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        ent_db = config['sql']['ent_db']
        # 解析 JDBC URL
        # jdbc:mysql://192.168.10.28:3306/nanshan_ent_qxb?...
        jdbc_url = ent_db['jdbc_url']
        host_port_db = jdbc_url.split("//")[1].split("?")[0]
        host_port, db_name = host_port_db.rsplit("/", 1)
        host, port = host_port.split(":")
        
        return pymysql.connect(
            host=host,
            port=int(port),
            user=ent_db['username'],
            password=ent_db['password'],
            database=db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        log_error(f"数据库连接失败: {e}")
        return None


def query_company(company_name: str, fields: str, limit: int) -> dict:
    """查询企业信息"""
    conn = get_db_connection()
    if not conn:
        return {"error": "数据库连接失败"}
    
    try:
        with conn.cursor() as cursor:
            # 构建查询
            field_list = fields if fields != "*" else "company_name, unified_code, legal_person, registered_capital, status"
            sql = f"""
                SELECT {field_list}
                FROM company_basic 
                WHERE company_name LIKE %s
                LIMIT %s
            """
            cursor.execute(sql, (f"%{company_name}%", limit))
            results = cursor.fetchall()
            
            return {
                "query": company_name,
                "count": len(results),
                "data": results
            }
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()


def main():
    args = parse_args()
    log_info(f"查询企业: {args.company_name}")
    
    result = query_company(args.company_name, args.fields, args.limit)
    
    # 输出 JSON
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    
    if "error" in result:
        sys.exit(1)


if __name__ == '__main__':
    main()
