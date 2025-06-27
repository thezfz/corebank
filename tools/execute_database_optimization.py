#!/usr/bin/env python3
"""
数脉银行数据库优化执行脚本

该脚本用于：
1. 执行数据库结构优化的所有阶段
2. 验证每个阶段的执行结果
3. 提供回滚选项
4. 生成优化报告
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent / "corebank-backend"
sys.path.insert(0, str(project_root))

class DatabaseOptimizer:
    """数据库优化执行器"""
    
    def __init__(self):
        self.backend_dir = Path(__file__).parent / "corebank-backend"
        self.optimization_phases = [
            {
                'name': '阶段1: 时间戳字段和触发器优化',
                'revision': '004_database_optimization_phase1',
                'description': '添加updated_at字段并创建自动更新触发器'
            },
            {
                'name': '阶段2: 索引冗余清理',
                'revision': '005_database_optimization_phase2',
                'description': '清理重复和冗余的索引'
            },
            {
                'name': '阶段3: 枚举类型替换',
                'revision': '006_database_optimization_phase3',
                'description': '将固定取值字段替换为PostgreSQL枚举类型'
            },
            {
                'name': '阶段4: 复式记账实现',
                'revision': '007_database_optimization_phase4',
                'description': '实现严谨的复式记账模式'
            },
            {
                'name': '阶段5: 数据迁移',
                'revision': '008_migrate_transaction_data',
                'description': '将现有交易数据迁移到新的复式记账结构'
            }
        ]
        
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
    
    def check_database_connection(self) -> bool:
        """检查数据库连接"""
        try:
            import psycopg2
            
            # 从环境变量读取数据库配置
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
            
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ 数据库连接成功: {version[0]}")
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def create_backup(self) -> str:
        """创建数据库备份"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"backup_before_optimization_{timestamp}.sql"
        
        try:
            # 构建pg_dump命令
            host = os.getenv('POSTGRES_HOST', 'localhost')
            if host == 'postgres':
                host = 'localhost'
            
            cmd = [
                'pg_dump',
                '-h', host,
                '-p', os.getenv('POSTGRES_PORT', '5432'),
                '-U', os.getenv('POSTGRES_USER', 'corebank_user'),
                '-d', os.getenv('POSTGRES_DB', 'corebank'),
                '-f', backup_file,
                '--verbose'
            ]
            
            # 设置密码环境变量
            env = os.environ.copy()
            env['PGPASSWORD'] = os.getenv('POSTGRES_PASSWORD', 'corebank_secure_password_2024')
            
            print(f"🔄 正在创建数据库备份: {backup_file}")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ 备份创建成功: {backup_file}")
                return backup_file
            else:
                print(f"❌ 备份创建失败: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ 备份创建异常: {e}")
            return None
    
    def run_alembic_upgrade(self, target_revision: str = None) -> bool:
        """运行Alembic升级"""
        try:
            os.chdir(self.backend_dir)
            
            if target_revision:
                cmd = ['alembic', 'upgrade', target_revision]
                print(f"🔄 执行数据库迁移到版本: {target_revision}")
            else:
                cmd = ['alembic', 'upgrade', 'head']
                print("🔄 执行数据库迁移到最新版本")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 数据库迁移成功")
                if result.stdout:
                    print(f"输出: {result.stdout}")
                return True
            else:
                print(f"❌ 数据库迁移失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 数据库迁移异常: {e}")
            return False
        finally:
            os.chdir(Path(__file__).parent)
    
    def get_current_revision(self) -> str:
        """获取当前数据库版本"""
        try:
            os.chdir(self.backend_dir)
            result = subprocess.run(['alembic', 'current'], capture_output=True, text=True)
            
            if result.returncode == 0:
                # 解析输出获取当前版本
                output = result.stdout.strip()
                if output:
                    # 输出格式通常是: "INFO  [alembic.runtime.migration] Context impl PostgreSQLImpl."
                    # 然后是: "INFO  [alembic.runtime.migration] Will assume transactional DDL."
                    # 最后是: "current_revision (head)"
                    lines = output.split('\n')
                    for line in lines:
                        if 'head' in line or len(line.strip()) == 32:  # revision ID length
                            return line.strip().split()[0]
                return "unknown"
            else:
                return "error"
                
        except Exception as e:
            print(f"❌ 获取当前版本异常: {e}")
            return "error"
        finally:
            os.chdir(Path(__file__).parent)
    
    def verify_optimization_phase(self, phase: dict) -> bool:
        """验证优化阶段的执行结果"""
        print(f"🔍 验证 {phase['name']} 的执行结果...")
        
        # 这里可以添加具体的验证逻辑
        # 例如检查表结构、索引、触发器等
        
        # 简单验证：检查当前版本是否包含该阶段的修订
        current_revision = self.get_current_revision()
        if phase['revision'].split('_')[0] in current_revision:
            print(f"✅ {phase['name']} 验证通过")
            return True
        else:
            print(f"❌ {phase['name']} 验证失败")
            return False
    
    def execute_optimization(self, start_phase: int = 0, end_phase: int = None) -> bool:
        """执行数据库优化"""
        
        if end_phase is None:
            end_phase = len(self.optimization_phases) - 1
        
        print("🏦 数脉银行数据库优化执行器")
        print("=" * 50)
        
        # 加载环境变量
        self.load_env_file()
        
        # 检查数据库连接
        if not self.check_database_connection():
            return False
        
        # 创建备份
        backup_file = self.create_backup()
        if not backup_file:
            print("❌ 无法创建备份，终止优化")
            return False
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 执行各个优化阶段
        for i in range(start_phase, end_phase + 1):
            phase = self.optimization_phases[i]
            
            print(f"\n🚀 开始执行 {phase['name']}")
            print(f"描述: {phase['description']}")
            
            # 执行迁移
            if not self.run_alembic_upgrade(phase['revision']):
                print(f"❌ {phase['name']} 执行失败，停止优化")
                return False
            
            # 验证结果
            if not self.verify_optimization_phase(phase):
                print(f"❌ {phase['name']} 验证失败，停止优化")
                return False
            
            print(f"✅ {phase['name']} 完成")
            time.sleep(1)  # 短暂暂停
        
        # 记录结束时间
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n🎉 数据库优化完成!")
        print(f"总耗时: {duration}")
        print(f"备份文件: {backup_file}")
        
        return True
    
    def rollback_optimization(self, target_revision: str = None) -> bool:
        """回滚数据库优化"""
        print("🔄 开始回滚数据库优化...")
        
        if target_revision is None:
            # 回滚到优化前的版本
            target_revision = "003_add_investment_features"
        
        try:
            os.chdir(self.backend_dir)
            cmd = ['alembic', 'downgrade', target_revision]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ 成功回滚到版本: {target_revision}")
                return True
            else:
                print(f"❌ 回滚失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 回滚异常: {e}")
            return False
        finally:
            os.chdir(Path(__file__).parent)


def main():
    """主函数"""
    optimizer = DatabaseOptimizer()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "rollback":
            target = sys.argv[2] if len(sys.argv) > 2 else None
            return 0 if optimizer.rollback_optimization(target) else 1
        elif command == "phase":
            if len(sys.argv) < 3:
                print("用法: python execute_database_optimization.py phase <phase_number>")
                return 1
            phase_num = int(sys.argv[2]) - 1
            return 0 if optimizer.execute_optimization(phase_num, phase_num) else 1
        elif command == "help":
            print("用法:")
            print("  python execute_database_optimization.py           # 执行所有优化阶段")
            print("  python execute_database_optimization.py phase N   # 执行第N个阶段")
            print("  python execute_database_optimization.py rollback  # 回滚所有优化")
            print("  python execute_database_optimization.py help      # 显示帮助")
            return 0
    
    # 默认执行所有优化
    return 0 if optimizer.execute_optimization() else 1


if __name__ == "__main__":
    sys.exit(main())
