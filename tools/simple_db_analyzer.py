#!/usr/bin/env python3
"""
简化的数据库分析工具
"""

import subprocess
import sys

def execute_sql(query):
    """执行SQL查询"""
    cmd = [
        "podman", "exec", "-it", "corebank_postgres",
        "psql", "-U", "corebank_user", "-d", "corebank",
        "-c", query
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"SQL执行错误: {e}")
        return ""

def analyze_table_structure(table_name):
    """分析单个表结构"""
    print(f"\n🏷️  表: {table_name}")
    print("-" * 50)
    
    # 获取表结构
    query = f"\\d {table_name}"
    result = execute_sql(query)
    print("📝 表结构:")
    print(result)

def main():
    if len(sys.argv) > 1:
        table_name = sys.argv[1]
        analyze_table_structure(table_name)
    else:
        print("用法: python simple_db_analyzer.py <table_name>")
        print("可用表名:")
        
        # 列出所有表
        result = execute_sql("\\dt")
        print(result)

if __name__ == "__main__":
    main()
