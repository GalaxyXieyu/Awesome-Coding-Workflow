#!/usr/bin/env python3
"""
向量库搜索脚本

用途：在 Milvus 向量库中搜索相似内容
调用：python search_vector.py "<query>" --collection <name> [--top_k 10]
输出：JSON 格式的搜索结果
"""
import sys
import json
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))


def log_error(msg: str):
    sys.stderr.write(f"ERROR: {msg}\n")


def log_info(msg: str):
    sys.stderr.write(f"INFO: {msg}\n")


# Collection 映射
COLLECTION_MAP = {
    "enterprise_kb": "enterprise_knowledge_base",
    "industry_kb": "industry_knowledge_base",
    "macro_kb": "macro_knowledge_base",
    "news_semantic": "news_semantic_vectors",
    "graph_entities": "graph_entities_vectors",
    "graph_relations": "graph_relations_vectors",
}


def parse_args():
    parser = argparse.ArgumentParser(description="向量库搜索")
    parser.add_argument("query", help="搜索查询文本")
    parser.add_argument("--collection", "-c", required=True, 
                       choices=list(COLLECTION_MAP.keys()),
                       help="Collection 名称")
    parser.add_argument("--top_k", "-k", type=int, default=10, help="返回结果数")
    return parser.parse_args()


def get_embedding(text: str) -> list:
    """获取文本向量（使用项目配置的 embedding 模型）"""
    try:
        # 实际项目中应该调用项目的 embedding 服务
        # 这里是示例，需要根据实际项目配置调整
        from src.infrastructure.llm import get_embedding_model
        model = get_embedding_model()
        return model.embed_query(text)
    except Exception as e:
        log_error(f"Embedding 失败: {e}")
        return None


def search_milvus(query: str, collection_key: str, top_k: int) -> dict:
    """在 Milvus 中搜索"""
    try:
        import yaml
        from pymilvus import connections, Collection
        
        # 读取配置
        config_path = PROJECT_ROOT / "backend/src/infrastructure/config/datasources.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        vector_config = config['vector']
        collection_config = vector_config['collections'][collection_key]
        
        # 连接 Milvus
        connections.connect(
            alias="default",
            host=vector_config['url'].split(":")[0],
            port=int(vector_config['url'].split(":")[1])
        )
        
        # 获取 collection
        collection = Collection(
            name=collection_config['name'],
            using="default"
        )
        collection.load()
        
        # 获取查询向量
        query_vector = get_embedding(query)
        if not query_vector:
            return {"error": "无法生成查询向量"}
        
        # 搜索
        search_params = {"metric_type": collection_config['dense_metric'], "params": {"ef": 64}}
        results = collection.search(
            data=[query_vector],
            anns_field=collection_config['dense_field'],
            param=search_params,
            limit=top_k,
            output_fields=[collection_config['text_field']]
        )
        
        # 格式化结果
        hits = []
        for hit in results[0]:
            hits.append({
                "id": hit.id,
                "score": float(hit.score),
                "text": hit.entity.get(collection_config['text_field'], "")
            })
        
        return {
            "query": query,
            "collection": collection_config['name'],
            "count": len(hits),
            "results": hits
        }
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            connections.disconnect("default")
        except:
            pass


def main():
    args = parse_args()
    log_info(f"搜索: {args.query} in {args.collection}")
    
    result = search_milvus(args.query, args.collection, args.top_k)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if "error" in result:
        sys.exit(1)


if __name__ == '__main__':
    main()
