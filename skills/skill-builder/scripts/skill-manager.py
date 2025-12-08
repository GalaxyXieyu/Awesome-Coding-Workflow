#!/usr/bin/env python3
"""
Skill Manager - 管理 Claude Code Skills 的命令行工具

功能：
- list: 列出所有 Skills
- show: 查看 Skill 详情
- create: 创建新 Skill
- history: 查看版本历史
- rollback: 回滚到指定版本
- diff: 对比两个版本
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# 配置
GLOBAL_SKILLS_DIR = Path.home() / ".claude" / "skills"
VERSION_DIR = Path.home() / ".claude" / ".skill-versions"


def ensure_version_dir():
    """确保版本目录存在"""
    VERSION_DIR.mkdir(parents=True, exist_ok=True)


def get_skill_version_dir(skill_name: str) -> Path:
    """获取 Skill 的版本目录"""
    return VERSION_DIR / skill_name


def list_skills(verbose: bool = False):
    """列出所有 Skills"""
    print("\n📦 全局 Skills (~/.claude/skills/)")
    print("-" * 50)
    
    if not GLOBAL_SKILLS_DIR.exists():
        print("  (空)")
        return
    
    skills = []
    for item in GLOBAL_SKILLS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            skill_file = item / "SKILL.md"
            if skill_file.exists():
                info = parse_skill_metadata(skill_file)
                skills.append({
                    "path": item,
                    "name": info.get("name", item.name),
                    "description": info.get("description", "无描述")
                })
    
    if not skills:
        print("  (空)")
        return
    
    for i, skill in enumerate(skills, 1):
        print(f"  {i}. {skill['name']}")
        print(f"     📝 {skill['description']}")
        if verbose:
            version_dir = get_skill_version_dir(skill['name'])
            if version_dir.exists():
                versions = list(version_dir.iterdir())
                print(f"     📚 版本数: {len(versions)}")
        print()


def parse_skill_metadata(skill_file: Path) -> dict:
    """解析 SKILL.md 的 YAML 头"""
    content = skill_file.read_text()
    metadata = {}
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_content = parts[1].strip()
            for line in yaml_content.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()
    
    return metadata


def show_skill(skill_name: str):
    """查看 Skill 详情"""
    skill_dir = GLOBAL_SKILLS_DIR / skill_name
    skill_file = skill_dir / "SKILL.md"
    
    if not skill_file.exists():
        print(f"❌ Skill 不存在: {skill_name}")
        return
    
    print(f"\n📄 Skill: {skill_name}")
    print("=" * 50)
    print(skill_file.read_text())
    
    # 显示版本信息
    version_dir = get_skill_version_dir(skill_name)
    if version_dir.exists():
        versions = sorted(version_dir.iterdir(), reverse=True)
        if versions:
            print("\n📚 版本历史")
            print("-" * 50)
            for v in versions[:5]:  # 只显示最近 5 个
                print(f"  - {v.name}")
            if len(versions) > 5:
                print(f"  ... 还有 {len(versions) - 5} 个版本")


def create_skill(skill_name: str, description: str = ""):
    """创建新 Skill"""
    skill_dir = GLOBAL_SKILLS_DIR / skill_name
    
    if skill_dir.exists():
        print(f"❌ Skill 已存在: {skill_name}")
        return
    
    # 创建目录结构
    skill_dir.mkdir(parents=True)
    (skill_dir / "scripts").mkdir()
    (skill_dir / "references").mkdir()
    
    # 创建 SKILL.md 模板
    template = f"""---
name: {skill_name}
description: {description or '待补充描述'}
---

# {skill_name}

## 触发场景
- 用户说"..."

## 执行步骤
1. 步骤1
2. 步骤2

## 边界条件
- 触发条件：...
- 不触发条件：...

## 踩坑清单
| 坑 | 表现 | 应对 |
|----|------|------|
| - | - | - |

## 约束条件
- 必须：...
- 禁止：...
"""
    
    (skill_dir / "SKILL.md").write_text(template)
    
    print(f"✅ 创建成功: {skill_dir}")
    print(f"   - SKILL.md")
    print(f"   - scripts/")
    print(f"   - references/")
    
    # 保存初始版本
    save_version(skill_name, "初始创建")


def save_version(skill_name: str, message: str = ""):
    """保存当前版本"""
    ensure_version_dir()
    
    skill_dir = GLOBAL_SKILLS_DIR / skill_name
    skill_file = skill_dir / "SKILL.md"
    
    if not skill_file.exists():
        print(f"❌ Skill 不存在: {skill_name}")
        return
    
    # 创建版本目录
    version_dir = get_skill_version_dir(skill_name)
    version_dir.mkdir(parents=True, exist_ok=True)
    
    # 版本名：时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version_file = version_dir / f"{timestamp}.md"
    
    # 复制当前内容
    content = skill_file.read_text()
    
    # 添加版本元信息
    version_content = f"""<!-- VERSION INFO
timestamp: {timestamp}
message: {message}
-->
{content}"""
    
    version_file.write_text(version_content)
    print(f"✅ 版本已保存: {version_file.name}")
    print(f"   消息: {message or '无'}")


def list_history(skill_name: str):
    """查看版本历史"""
    version_dir = get_skill_version_dir(skill_name)
    
    if not version_dir.exists():
        print(f"❌ 无版本历史: {skill_name}")
        return
    
    versions = sorted(version_dir.iterdir(), reverse=True)
    
    print(f"\n📚 {skill_name} 版本历史")
    print("-" * 50)
    
    for i, v in enumerate(versions):
        # 读取版本信息
        content = v.read_text()
        message = ""
        if "message:" in content:
            for line in content.split("\n"):
                if line.startswith("message:"):
                    message = line.split(":", 1)[1].strip()
                    break
        
        # 格式化时间
        ts = v.stem  # 20241208_141234
        try:
            dt = datetime.strptime(ts, "%Y%m%d_%H%M%S")
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = ts
        
        marker = "👉 " if i == 0 else "   "
        print(f"{marker}{i+1}. {time_str}")
        if message:
            print(f"      💬 {message}")


def rollback(skill_name: str, version_index: int = 1):
    """回滚到指定版本（1 = 最近一个版本）"""
    version_dir = get_skill_version_dir(skill_name)
    
    if not version_dir.exists():
        print(f"❌ 无版本历史: {skill_name}")
        return
    
    versions = sorted(version_dir.iterdir(), reverse=True)
    
    if version_index < 1 or version_index > len(versions):
        print(f"❌ 无效版本号: {version_index}（共 {len(versions)} 个版本）")
        return
    
    target_version = versions[version_index - 1]
    
    # 先保存当前版本
    save_version(skill_name, f"回滚前自动保存")
    
    # 读取目标版本内容（去掉版本元信息）
    content = target_version.read_text()
    if "<!-- VERSION INFO" in content:
        content = content.split("-->", 1)[1].strip()
    
    # 覆盖当前文件
    skill_file = GLOBAL_SKILLS_DIR / skill_name / "SKILL.md"
    skill_file.write_text(content)
    
    print(f"✅ 已回滚到: {target_version.name}")


def diff_versions(skill_name: str, v1: int = 1, v2: int = 2):
    """对比两个版本"""
    version_dir = get_skill_version_dir(skill_name)
    
    if not version_dir.exists():
        print(f"❌ 无版本历史: {skill_name}")
        return
    
    versions = sorted(version_dir.iterdir(), reverse=True)
    
    if v1 < 1 or v1 > len(versions) or v2 < 1 or v2 > len(versions):
        print(f"❌ 无效版本号（共 {len(versions)} 个版本）")
        return
    
    file1 = versions[v1 - 1]
    file2 = versions[v2 - 1]
    
    print(f"\n📊 对比: {file1.name} vs {file2.name}")
    print("-" * 50)
    
    # 使用 diff 命令
    os.system(f"diff -u '{file2}' '{file1}' | head -50")


def update_skill(skill_name: str, message: str = ""):
    """更新 Skill（保存版本后打开编辑）"""
    skill_file = GLOBAL_SKILLS_DIR / skill_name / "SKILL.md"
    
    if not skill_file.exists():
        print(f"❌ Skill 不存在: {skill_name}")
        return
    
    # 先保存当前版本
    save_version(skill_name, message or "更新前保存")
    
    print(f"✅ 版本已保存，可以安全编辑: {skill_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Skill Manager - 管理 Claude Code Skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  skill-manager list                  # 列出所有 Skills
  skill-manager list -v               # 详细列表
  skill-manager show my-skill         # 查看 Skill 详情
  skill-manager create my-skill       # 创建新 Skill
  skill-manager history my-skill      # 查看版本历史
  skill-manager save my-skill "描述"  # 保存当前版本
  skill-manager rollback my-skill 2   # 回滚到第 2 个版本
  skill-manager diff my-skill 1 2     # 对比版本 1 和 2
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # list
    list_parser = subparsers.add_parser("list", help="列出所有 Skills")
    list_parser.add_argument("-v", "--verbose", action="store_true", help="显示详细信息")
    
    # show
    show_parser = subparsers.add_parser("show", help="查看 Skill 详情")
    show_parser.add_argument("name", help="Skill 名称")
    
    # create
    create_parser = subparsers.add_parser("create", help="创建新 Skill")
    create_parser.add_argument("name", help="Skill 名称")
    create_parser.add_argument("-d", "--description", default="", help="描述")
    
    # history
    history_parser = subparsers.add_parser("history", help="查看版本历史")
    history_parser.add_argument("name", help="Skill 名称")
    
    # save
    save_parser = subparsers.add_parser("save", help="保存当前版本")
    save_parser.add_argument("name", help="Skill 名称")
    save_parser.add_argument("message", nargs="?", default="", help="版本消息")
    
    # rollback
    rollback_parser = subparsers.add_parser("rollback", help="回滚到指定版本")
    rollback_parser.add_argument("name", help="Skill 名称")
    rollback_parser.add_argument("version", type=int, nargs="?", default=1, help="版本号（1=最近）")
    
    # diff
    diff_parser = subparsers.add_parser("diff", help="对比两个版本")
    diff_parser.add_argument("name", help="Skill 名称")
    diff_parser.add_argument("v1", type=int, nargs="?", default=1, help="版本1")
    diff_parser.add_argument("v2", type=int, nargs="?", default=2, help="版本2")
    
    # update
    update_parser = subparsers.add_parser("update", help="更新前保存版本")
    update_parser.add_argument("name", help="Skill 名称")
    update_parser.add_argument("message", nargs="?", default="", help="版本消息")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_skills(args.verbose)
    elif args.command == "show":
        show_skill(args.name)
    elif args.command == "create":
        create_skill(args.name, args.description)
    elif args.command == "history":
        list_history(args.name)
    elif args.command == "save":
        save_version(args.name, args.message)
    elif args.command == "rollback":
        rollback(args.name, args.version)
    elif args.command == "diff":
        diff_versions(args.name, args.v1, args.v2)
    elif args.command == "update":
        update_skill(args.name, args.message)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
