#!/usr/bin/env python3
"""
CoreBank 数据库结构完整提取工具
提取数据库的完整结构信息，包括表、列、索引、约束、关系等
"""

import subprocess
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class DatabaseStructureAnalyzer:
    """数据库结构分析器"""
    
    def __init__(self, container_name="corebank_postgres", db_user="corebank_user", db_name="corebank"):
        self.container_name = container_name
        self.db_user = db_user
        self.db_name = db_name
        self.structure_data = {}
    
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
        
        # 数据库版本
        version_result = self.execute_sql("SELECT version();")
        
        # 数据库大小
        size_result = self.execute_sql(f"SELECT pg_size_pretty(pg_database_size('{self.db_name}'));")
        
        # 表数量
        table_count = self.execute_sql("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """)
        
        return {
            "database_name": self.db_name,
            "version": self._extract_value(version_result),
            "size": self._extract_value(size_result),
            "table_count": self._extract_value(table_count),
            "analysis_time": datetime.now().isoformat()
        }
    
    def _extract_value(self, result: str) -> str:
        """从查询结果中提取值"""
        lines = result.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('-') and not line.startswith('(') and not 'row' in line and not line.startswith('version') and not line.startswith('pg_size_pretty') and not line.startswith('count'):
                return line
        return ""
    
    def get_all_tables(self) -> List[str]:
        """获取所有表名"""
        print("📋 获取所有表名...")
        
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        
        result = self.execute_sql(query)
        tables = []
        
        for line in result.split('\n'):
            line = line.strip()
            if line and not line.startswith('-') and not line.startswith('table_name') and not line.endswith('rows)'):
                if line and not line.startswith('('):
                    tables.append(line)
        
        return tables
    
    def get_table_structure(self, table_name: str) -> Dict[str, Any]:
        """获取表的完整结构信息"""
        print(f"🔍 分析表: {table_name}")
        
        structure = {
            "table_name": table_name,
            "columns": self.get_table_columns(table_name),
            "constraints": self.get_table_constraints(table_name),
            "indexes": self.get_table_indexes(table_name),
            "foreign_keys": self.get_table_foreign_keys(table_name),
            "row_count": self.get_table_row_count(table_name),
            "table_size": self.get_table_size(table_name)
        }
        
        return structure
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表列信息"""
        query = f"""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            ordinal_position
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' 
        ORDER BY ordinal_position;
        """
        
        result = self.execute_sql(query)
        columns = []
        
        lines = result.split('\n')
        data_started = False
        
        for line in lines:
            line = line.strip()
            if '|' in line and data_started:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 8:
                    columns.append({
                        "name": parts[0],
                        "data_type": parts[1],
                        "nullable": parts[2] == "YES",
                        "default": parts[3] if parts[3] and parts[3] != '' else None,
                        "max_length": parts[4] if parts[4] and parts[4] != '' else None,
                        "precision": parts[5] if parts[5] and parts[5] != '' else None,
                        "scale": parts[6] if parts[6] and parts[6] != '' else None,
                        "position": int(parts[7]) if parts[7].isdigit() else 0
                    })
            elif line.startswith('column_name'):
                data_started = True
        
        return columns
    
    def get_table_constraints(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表约束信息"""
        query = f"""
        SELECT 
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name
        FROM information_schema.table_constraints tc
        LEFT JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = '{table_name}'
        ORDER BY tc.constraint_type, tc.constraint_name;
        """
        
        result = self.execute_sql(query)
        constraints = []
        
        lines = result.split('\n')
        data_started = False
        
        for line in lines:
            line = line.strip()
            if '|' in line and data_started:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    constraints.append({
                        "name": parts[0],
                        "type": parts[1],
                        "column": parts[2] if parts[2] and parts[2] != '' else None
                    })
            elif 'constraint_name' in line:
                data_started = True
        
        return constraints
    
    def get_table_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表索引信息"""
        query = f"""
        SELECT 
            indexname,
            indexdef
        FROM pg_indexes 
        WHERE tablename = '{table_name}'
        ORDER BY indexname;
        """
        
        result = self.execute_sql(query)
        indexes = []
        
        lines = result.split('\n')
        data_started = False
        
        for line in lines:
            line = line.strip()
            if '|' in line and data_started:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2:
                    indexes.append({
                        "name": parts[0],
                        "definition": parts[1]
                    })
            elif 'indexname' in line:
                data_started = True
        
        return indexes
    
    def get_table_foreign_keys(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表外键信息"""
        query = f"""
        SELECT 
            tc.constraint_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' 
        AND tc.table_name = '{table_name}'
        ORDER BY kcu.column_name;
        """
        
        result = self.execute_sql(query)
        foreign_keys = []
        
        lines = result.split('\n')
        data_started = False
        
        for line in lines:
            line = line.strip()
            if '|' in line and data_started:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4:
                    foreign_keys.append({
                        "constraint_name": parts[0],
                        "column": parts[1],
                        "referenced_table": parts[2],
                        "referenced_column": parts[3]
                    })
            elif 'constraint_name' in line:
                data_started = True
        
        return foreign_keys
    
    def get_table_row_count(self, table_name: str) -> int:
        """获取表行数"""
        query = f"SELECT COUNT(*) FROM {table_name};"
        result = self.execute_sql(query)
        
        for line in result.split('\n'):
            line = line.strip()
            if line.isdigit():
                return int(line)
        
        return 0
    
    def get_table_size(self, table_name: str) -> str:
        """获取表大小"""
        query = f"SELECT pg_size_pretty(pg_total_relation_size('{table_name}'));"
        result = self.execute_sql(query)
        return self._extract_value(result)

    def get_all_foreign_key_relationships(self) -> List[Dict[str, Any]]:
        """获取所有外键关系"""
        print("🔗 分析外键关系...")

        query = """
        SELECT
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            tc.constraint_name
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
        data_started = False

        for line in lines:
            line = line.strip()
            if '|' in line and data_started:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 5:
                    relationships.append({
                        "from_table": parts[0],
                        "from_column": parts[1],
                        "to_table": parts[2],
                        "to_column": parts[3],
                        "constraint_name": parts[4]
                    })
            elif 'table_name' in line:
                data_started = True

        return relationships

    def get_database_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        print("📈 获取数据库统计信息...")

        tables = self.get_all_tables()
        total_rows = 0
        table_stats = []

        for table in tables:
            row_count = self.get_table_row_count(table)
            table_size = self.get_table_size(table)
            total_rows += row_count

            table_stats.append({
                "table_name": table,
                "row_count": row_count,
                "size": table_size
            })

        return {
            "total_tables": len(tables),
            "total_rows": total_rows,
            "table_statistics": table_stats
        }

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
        for table in tables:
            structure = self.get_table_structure(table)
            table_structures.append(structure)

        # 获取外键关系
        foreign_key_relationships = self.get_all_foreign_key_relationships()

        # 获取统计信息
        statistics = self.get_database_statistics()

        # 组装完整结构
        complete_structure = {
            "database_info": db_info,
            "tables": table_structures,
            "foreign_key_relationships": foreign_key_relationships,
            "statistics": statistics
        }

        return complete_structure

    def save_structure_to_file(self, structure: Dict[str, Any], filename: Optional[str] = None) -> str:
        """保存结构到JSON文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"database_structure_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(structure, f, ensure_ascii=False, indent=2, default=str)

        print(f"✅ 数据库结构已保存到: {filename}")
        return filename

    def generate_markdown_report(self, structure: Dict[str, Any], filename: Optional[str] = None) -> str:
        """生成Markdown格式的分析报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"database_analysis_report_{timestamp}.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# CoreBank 数据库结构分析报告\n\n")

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
            f.write("| 表名 | 行数 | 大小 |\n")
            f.write("|------|------|------|\n")
            for table_stat in stats['table_statistics']:
                f.write(f"| {table_stat['table_name']} | {table_stat['row_count']} | {table_stat['size']} |\n")
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
                f.write(f"**行数**: {table['row_count']} | **大小**: {table['table_size']}\n\n")

                # 列信息
                f.write("#### 列信息\n\n")
                f.write("| 列名 | 数据类型 | 可空 | 默认值 |\n")
                f.write("|------|----------|------|--------|\n")
                for col in table['columns']:
                    nullable = "是" if col['nullable'] else "否"
                    default = col['default'] if col['default'] else "-"
                    f.write(f"| {col['name']} | {col['data_type']} | {nullable} | {default} |\n")
                f.write("\n")

                # 约束信息
                if table['constraints']:
                    f.write("#### 约束\n\n")
                    for constraint in table['constraints']:
                        f.write(f"- **{constraint['name']}** ({constraint['type']})")
                        if constraint['column']:
                            f.write(f": {constraint['column']}")
                        f.write("\n")
                    f.write("\n")

                # 索引信息
                if table['indexes']:
                    f.write("#### 索引\n\n")
                    for index in table['indexes']:
                        f.write(f"- **{index['name']}**\n")
                    f.write("\n")

                # 外键信息
                if table['foreign_keys']:
                    f.write("#### 外键\n\n")
                    for fk in table['foreign_keys']:
                        f.write(f"- **{fk['column']}** → {fk['referenced_table']}.{fk['referenced_column']}\n")
                    f.write("\n")

                f.write("---\n\n")

        print(f"✅ 分析报告已保存到: {filename}")
        return filename


def main():
    """主函数"""
    print("🔍 CoreBank 数据库结构完整提取工具")
    print("=" * 50)

    # 创建分析器
    analyzer = DatabaseStructureAnalyzer()

    try:
        # 执行完整分析
        structure = analyzer.analyze_complete_structure()

        # 保存JSON结构文件
        json_file = analyzer.save_structure_to_file(structure)

        # 生成Markdown报告
        md_file = analyzer.generate_markdown_report(structure)

        print("\n" + "=" * 50)
        print("✅ 分析完成！")
        print(f"📄 JSON结构文件: {json_file}")
        print(f"📋 Markdown报告: {md_file}")
        print("=" * 50)

        # 显示简要统计
        stats = structure['statistics']
        print(f"\n📊 数据库概览:")
        print(f"   总表数: {stats['total_tables']}")
        print(f"   总行数: {stats['total_rows']}")
        print(f"   外键关系: {len(structure['foreign_key_relationships'])}")

        print(f"\n📋 表列表:")
        for table_stat in stats['table_statistics']:
            print(f"   - {table_stat['table_name']}: {table_stat['row_count']} 行")

    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

    def get_all_foreign_key_relationships(self) -> List[Dict[str, Any]]:
        """获取所有外键关系"""
        print("🔗 分析外键关系...")

        query = """
        SELECT
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            tc.constraint_name
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
        data_started = False

        for line in lines:
            line = line.strip()
            if '|' in line and data_started:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 5:
                    relationships.append({
                        "from_table": parts[0],
                        "from_column": parts[1],
                        "to_table": parts[2],
                        "to_column": parts[3],
                        "constraint_name": parts[4]
                    })
            elif 'table_name' in line:
                data_started = True

        return relationships

    def get_database_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        print("📈 获取数据库统计信息...")

        tables = self.get_all_tables()
        total_rows = 0
        table_stats = []

        for table in tables:
            row_count = self.get_table_row_count(table)
            table_size = self.get_table_size(table)
            total_rows += row_count

            table_stats.append({
                "table_name": table,
                "row_count": row_count,
                "size": table_size
            })

        return {
            "total_tables": len(tables),
            "total_rows": total_rows,
            "table_statistics": table_stats
        }

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
        for table in tables:
            structure = self.get_table_structure(table)
            table_structures.append(structure)

        # 获取外键关系
        foreign_key_relationships = self.get_all_foreign_key_relationships()

        # 获取统计信息
        statistics = self.get_database_statistics()

        # 组装完整结构
        complete_structure = {
            "database_info": db_info,
            "tables": table_structures,
            "foreign_key_relationships": foreign_key_relationships,
            "statistics": statistics
        }

        return complete_structure

    def save_structure_to_file(self, structure: Dict[str, Any], filename: Optional[str] = None) -> str:
        """保存结构到JSON文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"database_structure_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(structure, f, ensure_ascii=False, indent=2, default=str)

        print(f"✅ 数据库结构已保存到: {filename}")
        return filename

    def generate_markdown_report(self, structure: Dict[str, Any], filename: Optional[str] = None) -> str:
        """生成Markdown格式的分析报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"database_analysis_report_{timestamp}.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# CoreBank 数据库结构分析报告\n\n")

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
            f.write("| 表名 | 行数 | 大小 |\n")
            f.write("|------|------|------|\n")
            for table_stat in stats['table_statistics']:
                f.write(f"| {table_stat['table_name']} | {table_stat['row_count']} | {table_stat['size']} |\n")
            f.write(f"\n**总计**: {stats['total_tables']} 个表，{stats['total_rows']} 行数据\n\n")

            # 表结构详情
            f.write("## 🏗️ 表结构详情\n\n")
            for table in structure['tables']:
                f.write(f"### {table['table_name']}\n\n")

                # 列信息
                f.write("#### 列信息\n\n")
                f.write("| 列名 | 数据类型 | 可空 | 默认值 | 说明 |\n")
                f.write("|------|----------|------|--------|------|\n")
                for col in table['columns']:
                    nullable = "是" if col['nullable'] else "否"
                    default = col['default'] if col['default'] else "-"
                    f.write(f"| {col['name']} | {col['data_type']} | {nullable} | {default} | - |\n")
                f.write("\n")

                # 约束信息
                if table['constraints']:
                    f.write("#### 约束\n\n")
                    for constraint in table['constraints']:
                        f.write(f"- **{constraint['name']}** ({constraint['type']})")
                        if constraint['column']:
                            f.write(f": {constraint['column']}")
                        f.write("\n")
                    f.write("\n")

                # 索引信息
                if table['indexes']:
                    f.write("#### 索引\n\n")
                    for index in table['indexes']:
                        f.write(f"- **{index['name']}**: {index['definition']}\n")
                    f.write("\n")

                # 外键信息
                if table['foreign_keys']:
                    f.write("#### 外键\n\n")
                    for fk in table['foreign_keys']:
                        f.write(f"- **{fk['column']}** → {fk['referenced_table']}.{fk['referenced_column']}\n")
                    f.write("\n")

                f.write(f"**行数**: {table['row_count']} | **大小**: {table['table_size']}\n\n")
                f.write("---\n\n")

            # 外键关系图
            f.write("## 🔗 外键关系\n\n")
            for rel in structure['foreign_key_relationships']:
                f.write(f"- {rel['from_table']}.{rel['from_column']} → {rel['to_table']}.{rel['to_column']}\n")

        print(f"✅ 分析报告已保存到: {filename}")
        return filename
