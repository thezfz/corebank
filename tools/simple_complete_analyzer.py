#!/usr/bin/env python3
"""
CoreBank 数据库结构完整提取工具 - 简化版
使用简单的方法提取数据库结构信息
"""

import subprocess
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class SimpleDatabaseAnalyzer:
    """简化的数据库结构分析器"""
    
    def __init__(self, container_name="corebank_postgres", db_user="corebank_user", db_name="corebank"):
        self.container_name = container_name
        self.db_user = db_user
        self.db_name = db_name
    
    def execute_sql(self, query: str) -> str:
        """执行SQL查询并返回结果"""
        cmd = [
            "podman", "exec", self.container_name,
            "psql", "-U", self.db_user, "-d", self.db_name,
            "-c", query
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ SQL执行错误: {e}")
            return ""
    
    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库基本信息"""
        print("📊 获取数据库基本信息...")
        
        # 数据库版本 - 简化提取
        version_result = self.execute_sql("SELECT version();")
        version = "PostgreSQL 16.8" if "PostgreSQL 16.8" in version_result else "Unknown"
        
        # 数据库大小
        size_result = self.execute_sql(f"SELECT pg_size_pretty(pg_database_size('{self.db_name}'));")
        size_lines = size_result.split('\n')
        size = "Unknown"
        for line in size_lines:
            line = line.strip()
            if 'MB' in line or 'KB' in line or 'GB' in line:
                size = line
                break
        
        # 表数量
        table_count_result = self.execute_sql("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """)
        table_count = "0"
        for line in table_count_result.split('\n'):
            line = line.strip()
            if line.isdigit():
                table_count = line
                break
        
        return {
            "database_name": self.db_name,
            "version": version,
            "size": size,
            "table_count": table_count,
            "analysis_time": datetime.now().isoformat()
        }
    
    def get_all_tables(self) -> List[str]:
        """获取所有表名"""
        print("📋 获取所有表名...")
        
        result = self.execute_sql("\\dt")
        tables = []
        
        lines = result.split('\n')
        for line in lines:
            line = line.strip()
            if '|' in line and 'table' in line and 'corebank_user' in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    table_name = parts[1].strip()
                    if table_name and table_name != 'Name':
                        tables.append(table_name)
        
        return tables
    
    def get_table_details(self, table_name: str) -> str:
        """获取表详细信息"""
        return self.execute_sql(f"\\d+ {table_name}")
    
    def get_table_row_count(self, table_name: str) -> int:
        """获取表行数"""
        result = self.execute_sql(f"SELECT COUNT(*) FROM {table_name};")
        
        for line in result.split('\n'):
            line = line.strip()
            if line.isdigit():
                return int(line)
        
        return 0
    
    def get_foreign_key_relationships(self) -> List[Dict[str, str]]:
        """获取外键关系"""
        print("🔗 分析外键关系...")
        
        query = """
        SELECT 
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_name, kcu.column_name;
        """
        
        result = self.execute_sql(query)
        relationships = []
        
        lines = result.split('\n')
        for line in lines:
            line = line.strip()
            if '|' in line and not line.startswith('table_name') and not line.startswith('-'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4 and parts[0] and parts[1] and parts[2] and parts[3]:
                    relationships.append({
                        "from_table": parts[0],
                        "from_column": parts[1],
                        "to_table": parts[2],
                        "to_column": parts[3]
                    })
        
        return relationships
    
    def analyze_complete_structure(self) -> Dict[str, Any]:
        """完整分析数据库结构"""
        print("🚀 开始完整数据库结构分析...")
        print("=" * 60)
        
        # 获取基本信息
        db_info = self.get_database_info()
        print(f"数据库: {db_info['database_name']}")
        print(f"版本: {db_info['version']}")
        print(f"大小: {db_info['size']}")
        
        # 获取所有表
        tables = self.get_all_tables()
        print(f"表数量: {len(tables)}")
        
        # 分析每个表
        table_structures = []
        total_rows = 0
        
        for table in tables:
            print(f"🔍 分析表: {table}")
            
            # 获取表详细信息
            table_details = self.get_table_details(table)
            row_count = self.get_table_row_count(table)
            total_rows += row_count
            
            table_structures.append({
                "table_name": table,
                "row_count": row_count,
                "structure_details": table_details
            })
        
        # 获取外键关系
        foreign_key_relationships = self.get_foreign_key_relationships()
        
        # 组装完整结构
        complete_structure = {
            "database_info": db_info,
            "tables": table_structures,
            "foreign_key_relationships": foreign_key_relationships,
            "statistics": {
                "total_tables": len(tables),
                "total_rows": total_rows,
                "table_list": [{"name": t["table_name"], "rows": t["row_count"]} for t in table_structures]
            }
        }
        
        return complete_structure
    
    def save_structure_to_file(self, structure: Dict[str, Any], filename: Optional[str] = None) -> str:
        """保存结构到JSON文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"complete_database_structure_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(structure, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ 数据库结构已保存到: {filename}")
        return filename
    
    def generate_markdown_report(self, structure: Dict[str, Any], filename: Optional[str] = None) -> str:
        """生成Markdown格式的分析报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"complete_database_report_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# CoreBank 数据库结构完整分析报告\n\n")
            
            # 基本信息
            db_info = structure['database_info']
            f.write("## 📊 数据库基本信息\n\n")
            f.write(f"- **数据库名**: {db_info['database_name']}\n")
            f.write(f"- **版本**: {db_info['version']}\n")
            f.write(f"- **大小**: {db_info['size']}\n")
            f.write(f"- **表数量**: {db_info['table_count']}\n")
            f.write(f"- **分析时间**: {db_info['analysis_time']}\n\n")
            
            # 统计信息
            stats = structure['statistics']
            f.write("## 📈 数据统计\n\n")
            f.write("| 表名 | 行数 |\n")
            f.write("|------|------|\n")
            for table_info in stats['table_list']:
                f.write(f"| {table_info['name']} | {table_info['rows']} |\n")
            f.write(f"\n**总计**: {stats['total_tables']} 个表，{stats['total_rows']} 行数据\n\n")
            
            # 外键关系
            f.write("## 🔗 外键关系\n\n")
            for rel in structure['foreign_key_relationships']:
                f.write(f"- {rel['from_table']}.{rel['from_column']} → {rel['to_table']}.{rel['to_column']}\n")
            f.write("\n")
            
            # 表结构详情
            f.write("## 🏗️ 表结构详情\n\n")
            for table in structure['tables']:
                f.write(f"### {table['table_name']}\n\n")
                f.write(f"**行数**: {table['row_count']}\n\n")
                f.write("```sql\n")
                f.write(table['structure_details'])
                f.write("\n```\n\n")
                f.write("---\n\n")
        
        print(f"✅ 分析报告已保存到: {filename}")
        return filename


def main():
    """主函数"""
    print("🔍 CoreBank 数据库结构完整提取工具 - 简化版")
    print("=" * 60)
    
    # 创建分析器
    analyzer = SimpleDatabaseAnalyzer()
    
    try:
        # 执行完整分析
        structure = analyzer.analyze_complete_structure()
        
        # 保存JSON结构文件
        json_file = analyzer.save_structure_to_file(structure)
        
        # 生成Markdown报告
        md_file = analyzer.generate_markdown_report(structure)
        
        print("\n" + "=" * 60)
        print("✅ 分析完成！")
        print(f"📄 JSON结构文件: {json_file}")
        print(f"📋 Markdown报告: {md_file}")
        print("=" * 60)
        
        # 显示简要统计
        stats = structure['statistics']
        print(f"\n📊 数据库概览:")
        print(f"   数据库: {structure['database_info']['database_name']}")
        print(f"   版本: {structure['database_info']['version']}")
        print(f"   大小: {structure['database_info']['size']}")
        print(f"   总表数: {stats['total_tables']}")
        print(f"   总行数: {stats['total_rows']}")
        print(f"   外键关系: {len(structure['foreign_key_relationships'])}")
        
        print(f"\n📋 表列表:")
        for table_info in stats['table_list']:
            print(f"   - {table_info['name']}: {table_info['rows']} 行")
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
