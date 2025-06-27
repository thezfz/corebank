#!/usr/bin/env python3
"""
数脉银行数据库ER图生成脚本

该脚本用于：
1. 基于数据库结构分析结果生成ER图
2. 使用Mermaid语法创建可视化图表
3. 展示表间关系和字段信息
"""

import json
from datetime import datetime

def load_database_structure(json_file: str) -> dict:
    """加载数据库结构JSON文件"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_mermaid_erd(data: dict) -> str:
    """生成Mermaid ER图"""
    
    mermaid_lines = [
        "erDiagram",
        ""
    ]
    
    tables = data['tables']
    
    # 定义表和字段
    for table_name, table_info in tables.items():
        if table_name == 'alembic_version':  # 跳过系统表
            continue
            
        # 表定义
        mermaid_lines.append(f"    {table_name.upper()} {{")
        
        for column in table_info['columns']:
            col_name = column['column_name']
            data_type = column['data_type']
            
            # 简化数据类型显示
            if data_type == 'character varying':
                data_type = 'varchar'
            elif data_type == 'timestamp with time zone':
                data_type = 'timestamp'
            elif data_type == 'uuid':
                data_type = 'uuid'
            elif data_type == 'numeric':
                data_type = 'decimal'
            
            # 添加约束标记
            constraints = []
            if column['is_primary_key']:
                constraints.append('PK')
            if column['is_foreign_key']:
                constraints.append('FK')
            if not column['is_nullable']:
                constraints.append('NOT NULL')
            
            constraint_str = f" {','.join(constraints)}" if constraints else ""
            
            mermaid_lines.append(f"        {data_type} {col_name}{constraint_str}")
        
        mermaid_lines.append("    }")
        mermaid_lines.append("")
    
    # 定义关系
    relationships = []
    
    for table_name, table_info in tables.items():
        if table_name == 'alembic_version':
            continue
            
        for column in table_info['columns']:
            if column['is_foreign_key'] and column['foreign_table']:
                foreign_table = column['foreign_table']
                if foreign_table != 'alembic_version':
                    # 确定关系类型
                    relationship_type = "||--o{"  # 一对多关系
                    
                    # 特殊关系处理
                    if table_name == 'user_profiles' and foreign_table == 'users':
                        relationship_type = "||--||"  # 一对一关系
                    
                    relationship = f"    {foreign_table.upper()} {relationship_type} {table_name.upper()} : has"
                    if relationship not in relationships:
                        relationships.append(relationship)
    
    mermaid_lines.extend(relationships)
    
    return "\n".join(mermaid_lines)

def generate_simplified_erd(data: dict) -> str:
    """生成简化版ER图，只显示主要字段"""
    
    mermaid_lines = [
        "erDiagram",
        ""
    ]
    
    tables = data['tables']
    
    # 定义核心字段映射
    core_fields = {
        'users': ['id', 'username', 'created_at'],
        'user_profiles': ['id', 'user_id', 'real_name', 'email', 'phone'],
        'accounts': ['id', 'user_id', 'account_number', 'account_type', 'balance'],
        'transactions': ['id', 'account_id', 'transaction_type', 'amount', 'timestamp'],
        'investment_products': ['id', 'product_code', 'name', 'product_type', 'risk_level'],
        'investment_holdings': ['id', 'user_id', 'product_id', 'shares', 'current_value'],
        'investment_transactions': ['id', 'user_id', 'product_id', 'transaction_type', 'amount'],
        'product_nav_history': ['id', 'product_id', 'nav_date', 'unit_nav'],
        'user_risk_assessments': ['id', 'user_id', 'risk_tolerance', 'assessment_score']
    }
    
    # 定义表和核心字段
    for table_name, table_info in tables.items():
        if table_name == 'alembic_version':
            continue
            
        mermaid_lines.append(f"    {table_name.upper()} {{")
        
        # 获取核心字段列表
        fields_to_show = core_fields.get(table_name, [])
        if not fields_to_show:
            # 如果没有预定义，显示前5个字段
            fields_to_show = [col['column_name'] for col in table_info['columns'][:5]]
        
        for column in table_info['columns']:
            if column['column_name'] not in fields_to_show:
                continue
                
            col_name = column['column_name']
            data_type = column['data_type']
            
            # 简化数据类型
            type_mapping = {
                'character varying': 'varchar',
                'timestamp with time zone': 'timestamp',
                'uuid': 'uuid',
                'numeric': 'decimal',
                'integer': 'int',
                'boolean': 'bool',
                'text': 'text',
                'date': 'date',
                'jsonb': 'json'
            }
            data_type = type_mapping.get(data_type, data_type)
            
            # 添加约束标记
            constraints = []
            if column['is_primary_key']:
                constraints.append('PK')
            if column['is_foreign_key']:
                constraints.append('FK')
            
            constraint_str = f" {','.join(constraints)}" if constraints else ""
            
            mermaid_lines.append(f"        {data_type} {col_name}{constraint_str}")
        
        mermaid_lines.append("    }")
        mermaid_lines.append("")
    
    # 定义关系
    relationships = []
    
    for table_name, table_info in tables.items():
        if table_name == 'alembic_version':
            continue
            
        for column in table_info['columns']:
            if column['is_foreign_key'] and column['foreign_table']:
                foreign_table = column['foreign_table']
                if foreign_table != 'alembic_version':
                    # 确定关系类型和标签
                    if table_name == 'user_profiles' and foreign_table == 'users':
                        relationship = f"    {foreign_table.upper()} ||--|| {table_name.upper()} : \"1:1\""
                    elif foreign_table == 'users':
                        relationship = f"    {foreign_table.upper()} ||--o{{ {table_name.upper()} : \"1:N\""
                    elif foreign_table == 'accounts':
                        relationship = f"    {foreign_table.upper()} ||--o{{ {table_name.upper()} : \"1:N\""
                    elif foreign_table == 'investment_products':
                        relationship = f"    {foreign_table.upper()} ||--o{{ {table_name.upper()} : \"1:N\""
                    elif foreign_table == 'investment_holdings':
                        relationship = f"    {foreign_table.upper()} ||--o{{ {table_name.upper()} : \"1:N\""
                    else:
                        relationship = f"    {foreign_table.upper()} ||--o{{ {table_name.upper()} : \"references\""
                    
                    if relationship not in relationships:
                        relationships.append(relationship)
    
    mermaid_lines.extend(relationships)
    
    return "\n".join(mermaid_lines)

def generate_business_module_erd(data: dict) -> str:
    """生成按业务模块分组的ER图"""
    
    mermaid_lines = [
        "erDiagram",
        "",
        "    %% 用户管理模块",
    ]
    
    # 用户管理模块
    user_tables = ['users', 'user_profiles', 'user_risk_assessments']
    for table_name in user_tables:
        if table_name in data['tables']:
            table_info = data['tables'][table_name]
            mermaid_lines.append(f"    {table_name.upper()} {{")
            
            # 显示关键字段
            key_fields = []
            for col in table_info['columns']:
                if (col['is_primary_key'] or col['is_foreign_key'] or 
                    col['column_name'] in ['username', 'real_name', 'email', 'risk_tolerance']):
                    key_fields.append(col)
            
            for column in key_fields[:6]:  # 限制显示字段数
                col_name = column['column_name']
                data_type = column['data_type'].replace('character varying', 'varchar')
                
                constraints = []
                if column['is_primary_key']:
                    constraints.append('PK')
                if column['is_foreign_key']:
                    constraints.append('FK')
                
                constraint_str = f" {','.join(constraints)}" if constraints else ""
                mermaid_lines.append(f"        {data_type} {col_name}{constraint_str}")
            
            mermaid_lines.append("    }")
    
    mermaid_lines.extend([
        "",
        "    %% 账户管理模块",
    ])
    
    # 账户管理模块
    account_tables = ['accounts', 'transactions']
    for table_name in account_tables:
        if table_name in data['tables']:
            table_info = data['tables'][table_name]
            mermaid_lines.append(f"    {table_name.upper()} {{")
            
            key_fields = []
            for col in table_info['columns']:
                if (col['is_primary_key'] or col['is_foreign_key'] or 
                    col['column_name'] in ['account_number', 'balance', 'amount', 'transaction_type']):
                    key_fields.append(col)
            
            for column in key_fields[:6]:
                col_name = column['column_name']
                data_type = column['data_type'].replace('character varying', 'varchar')
                
                constraints = []
                if column['is_primary_key']:
                    constraints.append('PK')
                if column['is_foreign_key']:
                    constraints.append('FK')
                
                constraint_str = f" {','.join(constraints)}" if constraints else ""
                mermaid_lines.append(f"        {data_type} {col_name}{constraint_str}")
            
            mermaid_lines.append("    }")
    
    mermaid_lines.extend([
        "",
        "    %% 投资理财模块",
    ])
    
    # 投资理财模块
    investment_tables = ['investment_products', 'investment_holdings', 'investment_transactions', 'product_nav_history']
    for table_name in investment_tables:
        if table_name in data['tables']:
            table_info = data['tables'][table_name]
            mermaid_lines.append(f"    {table_name.upper()} {{")
            
            key_fields = []
            for col in table_info['columns']:
                if (col['is_primary_key'] or col['is_foreign_key'] or 
                    col['column_name'] in ['product_code', 'name', 'shares', 'amount', 'unit_nav']):
                    key_fields.append(col)
            
            for column in key_fields[:6]:
                col_name = column['column_name']
                data_type = column['data_type'].replace('character varying', 'varchar')
                
                constraints = []
                if column['is_primary_key']:
                    constraints.append('PK')
                if column['is_foreign_key']:
                    constraints.append('FK')
                
                constraint_str = f" {','.join(constraints)}" if constraints else ""
                mermaid_lines.append(f"        {data_type} {col_name}{constraint_str}")
            
            mermaid_lines.append("    }")
    
    # 添加关系
    mermaid_lines.extend([
        "",
        "    %% 关系定义",
        "    USERS ||--|| USER_PROFILES : \"1:1\"",
        "    USERS ||--o{ ACCOUNTS : \"1:N\"",
        "    USERS ||--o{ USER_RISK_ASSESSMENTS : \"1:N\"",
        "    ACCOUNTS ||--o{ TRANSACTIONS : \"1:N\"",
        "    USERS ||--o{ INVESTMENT_HOLDINGS : \"1:N\"",
        "    INVESTMENT_PRODUCTS ||--o{ INVESTMENT_HOLDINGS : \"1:N\"",
        "    INVESTMENT_PRODUCTS ||--o{ INVESTMENT_TRANSACTIONS : \"1:N\"",
        "    INVESTMENT_PRODUCTS ||--o{ PRODUCT_NAV_HISTORY : \"1:N\"",
        "    INVESTMENT_HOLDINGS ||--o{ INVESTMENT_TRANSACTIONS : \"1:N\"",
    ])
    
    return "\n".join(mermaid_lines)

def main():
    """主函数"""
    print("🏦 数脉银行数据库ER图生成工具")
    print("=" * 50)
    
    # 查找最新的JSON文件
    import glob
    json_files = glob.glob("database_structure_*.json")
    if not json_files:
        print("未找到数据库结构JSON文件，请先运行 analyze_database_structure.py")
        return 1
    
    latest_file = max(json_files)
    print(f"使用数据文件: {latest_file}")
    
    # 加载数据
    data = load_database_structure(latest_file)
    
    # 生成不同版本的ER图
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. 完整ER图
    full_erd = generate_mermaid_erd(data)
    with open(f"database_erd_full_{timestamp}.mmd", 'w', encoding='utf-8') as f:
        f.write(full_erd)
    
    # 2. 简化ER图
    simple_erd = generate_simplified_erd(data)
    with open(f"database_erd_simple_{timestamp}.mmd", 'w', encoding='utf-8') as f:
        f.write(simple_erd)
    
    # 3. 业务模块ER图
    business_erd = generate_business_module_erd(data)
    with open(f"database_erd_business_{timestamp}.mmd", 'w', encoding='utf-8') as f:
        f.write(business_erd)
    
    print(f"\n📊 ER图生成完成:")
    print(f"- 完整版: database_erd_full_{timestamp}.mmd")
    print(f"- 简化版: database_erd_simple_{timestamp}.mmd")
    print(f"- 业务版: database_erd_business_{timestamp}.mmd")
    print("\n💡 可以使用Mermaid工具或在线编辑器查看这些图表")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
