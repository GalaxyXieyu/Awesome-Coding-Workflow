#!/usr/bin/env python3
"""
从项目中提取 Schema 并保存为元数据文件

用法: python extract_schema.py <project_path> <output_dir>
输出: Markdown 格式的 schema 文档
"""
import sys
import os
import ast
import re
from pathlib import Path


def find_python_files(project_path: str, patterns: list) -> list:
    """查找匹配模式的 Python 文件"""
    files = []
    for pattern in patterns:
        for f in Path(project_path).rglob(pattern):
            if "__pycache__" not in str(f) and ".venv" not in str(f):
                files.append(f)
    return files


def extract_sqlalchemy_models(file_path: Path) -> list:
    """从文件中提取 SQLAlchemy 模型定义"""
    models = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简单解析类定义
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查是否有 __tablename__
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == '__tablename__':
                                models.append({
                                    'class_name': node.name,
                                    'file': str(file_path),
                                    'line': node.lineno
                                })
    except Exception as e:
        pass
    return models


def extract_pydantic_models(file_path: Path) -> list:
    """从文件中提取 Pydantic 模型定义"""
    models = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查基类是否包含 BaseModel
                for base in node.bases:
                    if isinstance(base, ast.Name) and 'Model' in base.id:
                        models.append({
                            'class_name': node.name,
                            'file': str(file_path),
                            'line': node.lineno
                        })
                        break
    except Exception as e:
        pass
    return models


def generate_schema_doc(models: list, output_path: Path, title: str):
    """生成 schema 文档"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"自动提取于 {len(set(m['file'] for m in models))} 个文件\n\n")
        
        # 按文件分组
        by_file = {}
        for m in models:
            by_file.setdefault(m['file'], []).append(m)
        
        for file_path, file_models in by_file.items():
            f.write(f"## {Path(file_path).name}\n")
            f.write(f"路径: `{file_path}`\n\n")
            for m in file_models:
                f.write(f"- **{m['class_name']}** (line {m['line']})\n")
            f.write("\n")


def main():
    if len(sys.argv) < 3:
        print("用法: python extract_schema.py <project_path> <output_dir>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_dir = Path(sys.argv[2])
    
    print(f"=== 提取 Schema ===")
    print(f"项目: {project_path}")
    print(f"输出: {output_dir}")
    
    # 查找模型文件
    model_files = find_python_files(project_path, ["*model*.py", "*entity*.py", "*schema*.py"])
    
    # 提取 SQLAlchemy 模型
    sqlalchemy_models = []
    for f in model_files:
        sqlalchemy_models.extend(extract_sqlalchemy_models(f))
    
    if sqlalchemy_models:
        generate_schema_doc(sqlalchemy_models, output_dir / "sqlalchemy_models.md", "SQLAlchemy 模型")
        print(f"找到 {len(sqlalchemy_models)} 个 SQLAlchemy 模型")
    
    # 提取 Pydantic 模型
    pydantic_models = []
    for f in model_files:
        pydantic_models.extend(extract_pydantic_models(f))
    
    if pydantic_models:
        generate_schema_doc(pydantic_models, output_dir / "pydantic_models.md", "Pydantic 模型")
        print(f"找到 {len(pydantic_models)} 个 Pydantic 模型")
    
    print("=== 完成 ===")


if __name__ == '__main__':
    main()
