#!/usr/bin/env python3
"""
数脉银行数据库优化验证脚本

该脚本用于：
1. 验证数据库优化的执行结果
2. 检查数据完整性
3. 验证新功能是否正常工作
4. 生成验证报告
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from pathlib import Path

class OptimizationVerifier:
    """数据库优化验证器"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.verification_results = {
            'timestamp_fields': False,
            'redundant_indexes': False,
            'enum_types': False,
            'double_entry': False,
            'data_migration': False,
            'triggers': False,
            'constraints': False
        }
        
    def load_env_file(self, env_path: str = "corebank-backend/.env"):
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
    
    def connect_to_database(self) -> bool:
        """连接到数据库"""
        try:
            # 从环境变量读取数据库配置
            host = os.getenv('POSTGRES_HOST', 'localhost')
            if host == 'postgres':
                host = 'localhost'
            
            db_config = {
                'host': host,
                'port': int(os.getenv('POSTGRES_PORT', 5432)),
                'database': os.getenv('POSTGRES_DB', 'corebank'),
                'user': os.getenv('POSTGRES_USER', 'corebank_user'),
                'password': os.getenv('POSTGRES_PASSWORD', 'corebank_secure_password_2024')
            }
            
            self.connection = psycopg2.connect(**db_config)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            print("✅ 数据库连接成功")
            return True
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def verify_timestamp_fields(self) -> bool:
        """验证时间戳字段是否正确添加"""
        print("🔍 验证时间戳字段...")
        
        tables_to_check = ['accounts', 'users', 'transactions', 'product_nav_history']
        
        try:
            for table in tables_to_check:
                self.cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = 'updated_at'
                """, (table,))
                
                result = self.cursor.fetchone()
                if not result:
                    print(f"❌ 表 {table} 缺少 updated_at 字段")
                    return False
                else:
                    print(f"✅ 表 {table} 包含 updated_at 字段")
            
            self.verification_results['timestamp_fields'] = True
            return True
            
        except Exception as e:
            print(f"❌ 验证时间戳字段失败: {e}")
            return False
    
    def verify_redundant_indexes_removed(self) -> bool:
        """验证冗余索引是否已删除"""
        print("🔍 验证冗余索引清理...")
        
        redundant_indexes = [
            'idx_accounts_account_number',
            'idx_users_username',
            'idx_user_profiles_user_id'
        ]
        
        try:
            for index_name in redundant_indexes:
                self.cursor.execute("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE indexname = %s
                """, (index_name,))
                
                result = self.cursor.fetchone()
                if result:
                    print(f"❌ 冗余索引 {index_name} 仍然存在")
                    return False
                else:
                    print(f"✅ 冗余索引 {index_name} 已删除")
            
            self.verification_results['redundant_indexes'] = True
            return True
            
        except Exception as e:
            print(f"❌ 验证索引清理失败: {e}")
            return False
    
    def verify_enum_types(self) -> bool:
        """验证枚举类型是否正确创建和使用"""
        print("🔍 验证枚举类型...")
        
        expected_enums = [
            'account_type_enum',
            'transaction_type_enum',
            'transaction_status_enum',
            'product_type_enum',
            'investment_transaction_type_enum',
            'investment_transaction_status_enum',
            'holding_status_enum',
            'investment_experience_enum',
            'investment_goal_enum',
            'investment_horizon_enum'
        ]
        
        try:
            # 检查枚举类型是否存在
            self.cursor.execute("""
                SELECT typname 
                FROM pg_type 
                WHERE typtype = 'e'
            """)
            
            existing_enums = [row['typname'] for row in self.cursor.fetchall()]
            
            for enum_name in expected_enums:
                if enum_name in existing_enums:
                    print(f"✅ 枚举类型 {enum_name} 存在")
                else:
                    print(f"❌ 枚举类型 {enum_name} 不存在")
                    return False
            
            # 检查表字段是否使用了枚举类型
            enum_usage_checks = [
                ('accounts', 'account_type', 'account_type_enum'),
                ('transactions', 'transaction_type', 'transaction_type_enum'),
                ('transactions', 'status', 'transaction_status_enum'),
                ('investment_products', 'product_type', 'product_type_enum')
            ]
            
            for table, column, enum_type in enum_usage_checks:
                self.cursor.execute("""
                    SELECT data_type, udt_name
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = %s
                """, (table, column))
                
                result = self.cursor.fetchone()
                if result and result['udt_name'] == enum_type:
                    print(f"✅ 表 {table}.{column} 使用枚举类型 {enum_type}")
                else:
                    print(f"❌ 表 {table}.{column} 未使用枚举类型 {enum_type}")
                    return False
            
            self.verification_results['enum_types'] = True
            return True
            
        except Exception as e:
            print(f"❌ 验证枚举类型失败: {e}")
            return False
    
    def verify_double_entry_tables(self) -> bool:
        """验证复式记账表是否正确创建"""
        print("🔍 验证复式记账表结构...")
        
        try:
            # 检查 transaction_groups 表
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'transaction_groups'
            """)
            
            if not self.cursor.fetchone():
                print("❌ transaction_groups 表不存在")
                return False
            else:
                print("✅ transaction_groups 表存在")
            
            # 检查 transaction_entries 表
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'transaction_entries'
            """)
            
            if not self.cursor.fetchone():
                print("❌ transaction_entries 表不存在")
                return False
            else:
                print("✅ transaction_entries 表存在")
            
            # 检查 entry_type_enum
            self.cursor.execute("""
                SELECT typname 
                FROM pg_type 
                WHERE typname = 'entry_type_enum'
            """)
            
            if not self.cursor.fetchone():
                print("❌ entry_type_enum 枚举不存在")
                return False
            else:
                print("✅ entry_type_enum 枚举存在")
            
            self.verification_results['double_entry'] = True
            return True
            
        except Exception as e:
            print(f"❌ 验证复式记账表失败: {e}")
            return False
    
    def verify_data_migration(self) -> bool:
        """验证数据迁移是否成功"""
        print("🔍 验证数据迁移...")
        
        try:
            # 检查原始交易数据数量
            self.cursor.execute("SELECT COUNT(*) as count FROM transactions")
            original_count = self.cursor.fetchone()['count']
            
            # 检查迁移后的交易组数量
            self.cursor.execute("SELECT COUNT(*) as count FROM transaction_groups WHERE reference_id IS NOT NULL")
            migrated_groups = self.cursor.fetchone()['count']
            
            # 检查迁移后的交易条目数量
            self.cursor.execute("""
                SELECT COUNT(*) as count 
                FROM transaction_entries te
                JOIN transaction_groups tg ON te.transaction_group_id = tg.id
                WHERE tg.reference_id IS NOT NULL
            """)
            migrated_entries = self.cursor.fetchone()['count']
            
            print(f"原始交易数量: {original_count}")
            print(f"迁移的交易组数量: {migrated_groups}")
            print(f"迁移的交易条目数量: {migrated_entries}")
            
            if original_count == migrated_groups:
                print("✅ 交易数据迁移数量匹配")
                self.verification_results['data_migration'] = True
                return True
            else:
                print("❌ 交易数据迁移数量不匹配")
                return False
            
        except Exception as e:
            print(f"❌ 验证数据迁移失败: {e}")
            return False
    
    def verify_triggers(self) -> bool:
        """验证触发器是否正确创建"""
        print("🔍 验证触发器...")
        
        expected_triggers = [
            ('update_accounts_updated_at', 'accounts'),
            ('update_users_updated_at', 'users'),
            ('update_transactions_updated_at', 'transactions'),
            ('update_product_nav_history_updated_at', 'product_nav_history'),
            ('update_transaction_groups_updated_at', 'transaction_groups'),
            ('update_transaction_entries_updated_at', 'transaction_entries')
        ]
        
        try:
            for trigger_name, table_name in expected_triggers:
                self.cursor.execute("""
                    SELECT trigger_name 
                    FROM information_schema.triggers 
                    WHERE trigger_name = %s AND event_object_table = %s
                """, (trigger_name, table_name))
                
                if self.cursor.fetchone():
                    print(f"✅ 触发器 {trigger_name} 存在于表 {table_name}")
                else:
                    print(f"❌ 触发器 {trigger_name} 不存在于表 {table_name}")
                    return False
            
            self.verification_results['triggers'] = True
            return True
            
        except Exception as e:
            print(f"❌ 验证触发器失败: {e}")
            return False
    
    def verify_constraints(self) -> bool:
        """验证约束是否正确创建"""
        print("🔍 验证约束...")
        
        try:
            # 检查 transaction_entries 表的检查约束
            self.cursor.execute("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'transaction_entries' 
                AND constraint_type = 'CHECK'
                AND constraint_name = 'ck_transaction_entries_amount_positive'
            """)
            
            if self.cursor.fetchone():
                print("✅ transaction_entries 金额正数约束存在")
            else:
                print("❌ transaction_entries 金额正数约束不存在")
                return False
            
            # 检查外键约束
            foreign_key_checks = [
                ('transaction_entries', 'fk_transaction_entries_group'),
                ('transaction_entries', 'fk_transaction_entries_account')
            ]
            
            for table, constraint in foreign_key_checks:
                self.cursor.execute("""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = %s 
                    AND constraint_type = 'FOREIGN KEY'
                    AND constraint_name = %s
                """, (table, constraint))
                
                if self.cursor.fetchone():
                    print(f"✅ 外键约束 {constraint} 存在于表 {table}")
                else:
                    print(f"❌ 外键约束 {constraint} 不存在于表 {table}")
                    return False
            
            self.verification_results['constraints'] = True
            return True
            
        except Exception as e:
            print(f"❌ 验证约束失败: {e}")
            return False
    
    def generate_verification_report(self) -> str:
        """生成验证报告"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = [
            "# 数脉银行数据库优化验证报告",
            f"生成时间: {timestamp}",
            "",
            "## 验证结果概览",
            ""
        ]
        
        total_checks = len(self.verification_results)
        passed_checks = sum(self.verification_results.values())
        
        report.append(f"总检查项: {total_checks}")
        report.append(f"通过检查: {passed_checks}")
        report.append(f"失败检查: {total_checks - passed_checks}")
        report.append(f"成功率: {passed_checks/total_checks*100:.1f}%")
        report.append("")
        
        report.append("## 详细验证结果")
        report.append("")
        
        check_descriptions = {
            'timestamp_fields': '时间戳字段添加',
            'redundant_indexes': '冗余索引清理',
            'enum_types': '枚举类型替换',
            'double_entry': '复式记账表创建',
            'data_migration': '数据迁移',
            'triggers': '触发器创建',
            'constraints': '约束创建'
        }
        
        for check, passed in self.verification_results.items():
            status = "✅ 通过" if passed else "❌ 失败"
            description = check_descriptions.get(check, check)
            report.append(f"- {description}: {status}")
        
        report.append("")
        
        if all(self.verification_results.values()):
            report.append("## 🎉 总结")
            report.append("所有验证检查都已通过！数据库优化成功完成。")
        else:
            report.append("## ⚠️ 总结")
            report.append("部分验证检查失败，请检查上述详细结果并修复问题。")
        
        return "\n".join(report)
    
    def run_verification(self) -> bool:
        """运行完整的验证流程"""
        print("🏦 数脉银行数据库优化验证器")
        print("=" * 50)
        
        # 加载环境变量
        self.load_env_file()
        
        # 连接数据库
        if not self.connect_to_database():
            return False
        
        # 执行各项验证
        verification_steps = [
            self.verify_timestamp_fields,
            self.verify_redundant_indexes_removed,
            self.verify_enum_types,
            self.verify_double_entry_tables,
            self.verify_data_migration,
            self.verify_triggers,
            self.verify_constraints
        ]
        
        for step in verification_steps:
            try:
                step()
                print()
            except Exception as e:
                print(f"❌ 验证步骤异常: {e}")
                print()
        
        # 生成报告
        report = self.generate_verification_report()
        
        # 保存报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"database_optimization_verification_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📊 验证报告已保存: {report_file}")
        
        # 显示简要结果
        passed_checks = sum(self.verification_results.values())
        total_checks = len(self.verification_results)
        
        if passed_checks == total_checks:
            print("🎉 所有验证检查通过！")
            return True
        else:
            print(f"⚠️ {total_checks - passed_checks} 个检查失败")
            return False
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


def main():
    """主函数"""
    verifier = OptimizationVerifier()
    
    try:
        success = verifier.run_verification()
        return 0 if success else 1
    finally:
        verifier.close_connection()


if __name__ == "__main__":
    sys.exit(main())
