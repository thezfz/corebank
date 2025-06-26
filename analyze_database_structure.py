#!/usr/bin/env python3
"""
数脉银行数据库结构分析脚本

该脚本用于：
1. 提取数据库的详细结构信息
2. 分析表结构的合理性
3. 检查索引优化情况
4. 分析外键关系
5. 生成结构分析报告
"""

import os
import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent / "corebank-backend"
sys.path.insert(0, str(project_root))

@dataclass
class ColumnInfo:
    """列信息数据类"""
    column_name: str
    data_type: str
    is_nullable: bool
    column_default: Optional[str]
    character_maximum_length: Optional[int]
    numeric_precision: Optional[int]
    numeric_scale: Optional[int]
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_table: Optional[str] = None
    foreign_column: Optional[str] = None

@dataclass
class IndexInfo:
    """索引信息数据类"""
    index_name: str
    table_name: str
    column_names: List[str]
    is_unique: bool
    is_primary: bool
    index_type: str

@dataclass
class TableInfo:
    """表信息数据类"""
    table_name: str
    columns: List[ColumnInfo]
    indexes: List[IndexInfo]
    row_count: int
    table_size: str
    constraints: List[Dict[str, Any]]

class DatabaseAnalyzer:
    """数据库结构分析器"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.analysis_results = {}
        
    def connect_to_database(self) -> bool:
        """连接到数据库"""
        try:
            # 从环境变量或.env文件读取数据库配置
            # 如果在容器外运行，使用localhost而不是postgres
            host = os.getenv('POSTGRES_HOST', 'localhost')
            if host == 'postgres':
                host = 'localhost'  # 容器外访问使用localhost

            db_config = {
                'host': host,
                'port': int(os.getenv('POSTGRES_PORT', 5432)),
                'database': os.getenv('POSTGRES_DB', 'corebank'),
                'user': os.getenv('POSTGRES_USER', 'corebank_user'),
                'password': os.getenv('POSTGRES_PASSWORD', 'corebank_secure_password_2024')
            }
            
            print(f"正在连接数据库: {db_config['host']}:{db_config['port']}/{db_config['database']}")
            
            self.connection = psycopg2.connect(**db_config)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            # 测试连接
            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()
            print(f"数据库连接成功: {version['version']}")
            
            return True
            
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False
    
    def get_all_tables(self) -> List[str]:
        """获取所有用户表"""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        
        self.cursor.execute(query)
        tables = [row['table_name'] for row in self.cursor.fetchall()]
        print(f"发现 {len(tables)} 个表: {', '.join(tables)}")
        return tables
    
    def get_table_columns(self, table_name: str) -> List[ColumnInfo]:
        """获取表的列信息"""
        query = """
        SELECT 
            c.column_name,
            c.data_type,
            c.is_nullable = 'YES' as is_nullable,
            c.column_default,
            c.character_maximum_length,
            c.numeric_precision,
            c.numeric_scale,
            CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END as is_primary_key,
            CASE WHEN fk.column_name IS NOT NULL THEN true ELSE false END as is_foreign_key,
            fk.foreign_table_name as foreign_table,
            fk.foreign_column_name as foreign_column
        FROM information_schema.columns c
        LEFT JOIN (
            SELECT ku.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage ku 
                ON tc.constraint_name = ku.constraint_name
            WHERE tc.table_name = %s 
            AND tc.constraint_type = 'PRIMARY KEY'
        ) pk ON c.column_name = pk.column_name
        LEFT JOIN (
            SELECT 
                ku.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage ku 
                ON tc.constraint_name = ku.constraint_name
            JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_name = %s 
            AND tc.constraint_type = 'FOREIGN KEY'
        ) fk ON c.column_name = fk.column_name
        WHERE c.table_name = %s
        ORDER BY c.ordinal_position;
        """
        
        self.cursor.execute(query, (table_name, table_name, table_name))
        columns = []
        
        for row in self.cursor.fetchall():
            column = ColumnInfo(
                column_name=row['column_name'],
                data_type=row['data_type'],
                is_nullable=row['is_nullable'],
                column_default=row['column_default'],
                character_maximum_length=row['character_maximum_length'],
                numeric_precision=row['numeric_precision'],
                numeric_scale=row['numeric_scale'],
                is_primary_key=row['is_primary_key'],
                is_foreign_key=row['is_foreign_key'],
                foreign_table=row['foreign_table'],
                foreign_column=row['foreign_column']
            )
            columns.append(column)
        
        return columns
    
    def get_table_indexes(self, table_name: str) -> List[IndexInfo]:
        """获取表的索引信息"""
        query = """
        SELECT 
            i.indexname as index_name,
            i.tablename as table_name,
            array_agg(a.attname ORDER BY a.attnum) as column_names,
            ix.indisunique as is_unique,
            ix.indisprimary as is_primary,
            am.amname as index_type
        FROM pg_indexes i
        JOIN pg_class c ON c.relname = i.tablename
        JOIN pg_index ix ON ix.indexrelid = (
            SELECT oid FROM pg_class WHERE relname = i.indexname
        )
        JOIN pg_class ic ON ic.oid = ix.indexrelid
        JOIN pg_am am ON am.oid = ic.relam
        JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = ANY(ix.indkey)
        WHERE i.tablename = %s
        AND i.schemaname = 'public'
        GROUP BY i.indexname, i.tablename, ix.indisunique, ix.indisprimary, am.amname
        ORDER BY i.indexname;
        """
        
        self.cursor.execute(query, (table_name,))
        indexes = []
        
        for row in self.cursor.fetchall():
            index = IndexInfo(
                index_name=row['index_name'],
                table_name=row['table_name'],
                column_names=row['column_names'],
                is_unique=row['is_unique'],
                is_primary=row['is_primary'],
                index_type=row['index_type']
            )
            indexes.append(index)
        
        return indexes
    
    def get_table_constraints(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表的约束信息"""
        query = """
        SELECT 
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            rc.match_option,
            rc.update_rule,
            rc.delete_rule
        FROM information_schema.table_constraints tc
        LEFT JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
        LEFT JOIN information_schema.constraint_column_usage ccu 
            ON ccu.constraint_name = tc.constraint_name
        LEFT JOIN information_schema.referential_constraints rc 
            ON tc.constraint_name = rc.constraint_name
        WHERE tc.table_name = %s
        ORDER BY tc.constraint_type, tc.constraint_name;
        """
        
        self.cursor.execute(query, (table_name,))
        constraints = []
        
        for row in self.cursor.fetchall():
            constraint = {
                'constraint_name': row['constraint_name'],
                'constraint_type': row['constraint_type'],
                'column_name': row['column_name'],
                'foreign_table_name': row['foreign_table_name'],
                'foreign_column_name': row['foreign_column_name'],
                'match_option': row['match_option'],
                'update_rule': row['update_rule'],
                'delete_rule': row['delete_rule']
            }
            constraints.append(constraint)
        
        return constraints
    
    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """获取表的统计信息"""
        # 获取行数
        self.cursor.execute(f"SELECT COUNT(*) as row_count FROM {table_name};")
        row_count = self.cursor.fetchone()['row_count']
        
        # 获取表大小
        self.cursor.execute("""
            SELECT pg_size_pretty(pg_total_relation_size(%s)) as table_size;
        """, (table_name,))
        table_size = self.cursor.fetchone()['table_size']
        
        return {
            'row_count': row_count,
            'table_size': table_size
        }

    def analyze_table(self, table_name: str) -> TableInfo:
        """分析单个表的完整信息"""
        print(f"正在分析表: {table_name}")

        columns = self.get_table_columns(table_name)
        indexes = self.get_table_indexes(table_name)
        constraints = self.get_table_constraints(table_name)
        stats = self.get_table_stats(table_name)

        table_info = TableInfo(
            table_name=table_name,
            columns=columns,
            indexes=indexes,
            row_count=stats['row_count'],
            table_size=stats['table_size'],
            constraints=constraints
        )

        return table_info

    def analyze_all_tables(self) -> Dict[str, TableInfo]:
        """分析所有表"""
        tables = self.get_all_tables()
        table_infos = {}

        for table_name in tables:
            try:
                table_info = self.analyze_table(table_name)
                table_infos[table_name] = table_info
            except Exception as e:
                print(f"分析表 {table_name} 时出错: {e}")
                continue

        return table_infos

    def analyze_database_design(self, table_infos: Dict[str, TableInfo]) -> Dict[str, Any]:
        """分析数据库设计的合理性"""
        analysis = {
            'summary': {},
            'issues': [],
            'recommendations': [],
            'strengths': []
        }

        total_tables = len(table_infos)
        total_columns = sum(len(table.columns) for table in table_infos.values())
        total_indexes = sum(len(table.indexes) for table in table_infos.values())
        total_rows = sum(table.row_count for table in table_infos.values())

        analysis['summary'] = {
            'total_tables': total_tables,
            'total_columns': total_columns,
            'total_indexes': total_indexes,
            'total_rows': total_rows
        }

        # 分析每个表
        for table_name, table_info in table_infos.items():
            self._analyze_table_design(table_name, table_info, analysis)

        # 分析表间关系
        self._analyze_relationships(table_infos, analysis)

        return analysis

    def _analyze_table_design(self, table_name: str, table_info: TableInfo, analysis: Dict[str, Any]):
        """分析单个表的设计"""

        # 检查主键
        primary_keys = [col for col in table_info.columns if col.is_primary_key]
        if not primary_keys:
            analysis['issues'].append(f"表 {table_name} 缺少主键")
        elif len(primary_keys) > 1:
            analysis['strengths'].append(f"表 {table_name} 使用复合主键")

        # 检查UUID主键
        uuid_pk = any(col.is_primary_key and col.data_type == 'uuid' for col in table_info.columns)
        if uuid_pk:
            analysis['strengths'].append(f"表 {table_name} 使用UUID主键，有利于分布式系统")

        # 检查时间戳字段
        timestamp_fields = [col for col in table_info.columns if 'timestamp' in col.data_type.lower()]
        if len(timestamp_fields) >= 2:
            analysis['strengths'].append(f"表 {table_name} 包含创建和更新时间戳")
        elif len(timestamp_fields) == 1:
            analysis['recommendations'].append(f"表 {table_name} 建议添加更新时间戳字段")
        else:
            analysis['issues'].append(f"表 {table_name} 缺少时间戳字段")

        # 检查索引覆盖
        indexed_columns = set()
        for index in table_info.indexes:
            indexed_columns.update(index.column_names)

        foreign_key_columns = [col.column_name for col in table_info.columns if col.is_foreign_key]
        unindexed_fks = [fk for fk in foreign_key_columns if fk not in indexed_columns]

        if unindexed_fks:
            analysis['issues'].append(f"表 {table_name} 的外键字段 {unindexed_fks} 缺少索引")

        # 检查数据类型合理性
        for col in table_info.columns:
            if col.data_type == 'text' and col.column_name in ['email', 'phone', 'code']:
                analysis['recommendations'].append(
                    f"表 {table_name} 的 {col.column_name} 字段建议使用VARCHAR限制长度"
                )

            if col.data_type == 'numeric' and col.numeric_precision and col.numeric_precision > 19:
                analysis['issues'].append(
                    f"表 {table_name} 的 {col.column_name} 字段精度过高，可能影响性能"
                )

        # 检查表大小
        if table_info.row_count > 100000:
            analysis['recommendations'].append(f"表 {table_name} 数据量较大({table_info.row_count}行)，建议考虑分区")

    def _analyze_relationships(self, table_infos: Dict[str, TableInfo], analysis: Dict[str, Any]):
        """分析表间关系"""

        # 统计外键关系
        foreign_keys = {}
        for table_name, table_info in table_infos.items():
            for col in table_info.columns:
                if col.is_foreign_key:
                    if col.foreign_table not in foreign_keys:
                        foreign_keys[col.foreign_table] = []
                    foreign_keys[col.foreign_table].append({
                        'from_table': table_name,
                        'from_column': col.column_name,
                        'to_column': col.foreign_column
                    })

        # 检查引用完整性
        for referenced_table, references in foreign_keys.items():
            if referenced_table not in table_infos:
                analysis['issues'].append(f"外键引用的表 {referenced_table} 不存在")
            else:
                analysis['strengths'].append(
                    f"表 {referenced_table} 被 {len(references)} 个表引用，关系设计良好"
                )

        # 检查孤立表
        referenced_tables = set(foreign_keys.keys())
        referencing_tables = set()
        for table_info in table_infos.values():
            if any(col.is_foreign_key for col in table_info.columns):
                referencing_tables.add(table_info.table_name)

        all_tables = set(table_infos.keys())
        isolated_tables = all_tables - referenced_tables - referencing_tables

        if isolated_tables:
            analysis['recommendations'].append(
                f"表 {list(isolated_tables)} 没有外键关系，请确认是否需要建立关联"
            )

    def generate_report(self, table_infos: Dict[str, TableInfo], analysis: Dict[str, Any]) -> str:
        """生成分析报告"""
        report = []
        report.append("# 数脉银行数据库结构分析报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # 概览
        report.append("## 📊 数据库概览")
        summary = analysis['summary']
        report.append(f"- 总表数: {summary['total_tables']}")
        report.append(f"- 总字段数: {summary['total_columns']}")
        report.append(f"- 总索引数: {summary['total_indexes']}")
        report.append(f"- 总记录数: {summary['total_rows']:,}")
        report.append("")

        # 表结构详情
        report.append("## 📋 表结构详情")
        for table_name, table_info in sorted(table_infos.items()):
            report.append(f"### {table_name}")
            report.append(f"- 记录数: {table_info.row_count:,}")
            report.append(f"- 存储大小: {table_info.table_size}")
            report.append(f"- 字段数: {len(table_info.columns)}")
            report.append(f"- 索引数: {len(table_info.indexes)}")

            # 字段信息
            report.append("\n#### 字段信息")
            report.append("| 字段名 | 类型 | 可空 | 默认值 | 主键 | 外键 |")
            report.append("|--------|------|------|--------|------|------|")

            for col in table_info.columns:
                nullable = "是" if col.is_nullable else "否"
                pk = "✓" if col.is_primary_key else ""
                fk = f"→{col.foreign_table}.{col.foreign_column}" if col.is_foreign_key else ""
                default = col.column_default or ""
                if len(default) > 20:
                    default = default[:20] + "..."

                report.append(f"| {col.column_name} | {col.data_type} | {nullable} | {default} | {pk} | {fk} |")

            # 索引信息
            if table_info.indexes:
                report.append("\n#### 索引信息")
                report.append("| 索引名 | 字段 | 唯一 | 类型 |")
                report.append("|--------|------|------|------|")

                for idx in table_info.indexes:
                    unique = "✓" if idx.is_unique else ""
                    columns = ", ".join(idx.column_names)
                    report.append(f"| {idx.index_name} | {columns} | {unique} | {idx.index_type} |")

            report.append("")

        # 设计分析
        report.append("## 🔍 设计分析")

        if analysis['strengths']:
            report.append("### ✅ 设计优点")
            for strength in analysis['strengths']:
                report.append(f"- {strength}")
            report.append("")

        if analysis['issues']:
            report.append("### ⚠️ 发现问题")
            for issue in analysis['issues']:
                report.append(f"- {issue}")
            report.append("")

        if analysis['recommendations']:
            report.append("### 💡 优化建议")
            for rec in analysis['recommendations']:
                report.append(f"- {rec}")
            report.append("")

        return "\n".join(report)

    def save_results(self, table_infos: Dict[str, TableInfo], analysis: Dict[str, Any]):
        """保存分析结果"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 保存JSON格式的详细数据
        json_data = {
            'timestamp': timestamp,
            'tables': {name: asdict(info) for name, info in table_infos.items()},
            'analysis': analysis
        }

        json_file = f"database_structure_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2, default=str)

        # 保存Markdown格式的报告
        report = self.generate_report(table_infos, analysis)
        report_file = f"database_analysis_report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"分析结果已保存:")
        print(f"- 详细数据: {json_file}")
        print(f"- 分析报告: {report_file}")

    def close_connection(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("数据库连接已关闭")


def load_env_file(env_path: str = "corebank-backend/.env"):
    """加载.env文件中的环境变量"""
    if not os.path.exists(env_path):
        print(f"警告: 未找到环境变量文件 {env_path}")
        return

    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value


def main():
    """主函数"""
    print("🏦 数脉银行数据库结构分析工具")
    print("=" * 50)

    # 加载环境变量
    load_env_file()

    # 创建分析器
    analyzer = DatabaseAnalyzer()

    try:
        # 连接数据库
        if not analyzer.connect_to_database():
            return 1

        # 分析所有表
        print("\n开始分析数据库结构...")
        table_infos = analyzer.analyze_all_tables()

        if not table_infos:
            print("未找到任何表")
            return 1

        # 分析设计合理性
        print("\n开始分析设计合理性...")
        analysis = analyzer.analyze_database_design(table_infos)

        # 保存结果
        analyzer.save_results(table_infos, analysis)

        # 显示简要统计
        print(f"\n📊 分析完成!")
        print(f"- 分析了 {len(table_infos)} 个表")
        print(f"- 发现 {len(analysis['issues'])} 个问题")
        print(f"- 提出 {len(analysis['recommendations'])} 个建议")
        print(f"- 识别 {len(analysis['strengths'])} 个优点")

        return 0

    except Exception as e:
        print(f"分析过程中出错: {e}")
        return 1

    finally:
        analyzer.close_connection()


if __name__ == "__main__":
    sys.exit(main())
