#!/usr/bin/env python3
"""测试运行脚本"""
import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """运行命令并返回是否成功"""
    print(f"\n🔄 {description}")
    print(f"执行命令: {command}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - 成功")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"❌ {description} - 失败")
        if result.stderr:
            print(result.stderr)
        if result.stdout:
            print(result.stdout)
        return False


def main():
    """主函数"""
    print("🏆 CoreBank 测试金字塔执行")
    print("=" * 50)
    
    # 确保在正确的目录
    backend_dir = Path(__file__).parent.parent
    
    success_count = 0
    total_tests = 0
    
    # 1. 单元测试 (最多)
    print("\n📊 第一层：单元测试 (Unit Tests)")
    print("-" * 30)
    
    unit_tests = [
        ("pytest tests/services/ -v -m unit", "服务层单元测试"),
        ("pytest tests/repositories/ -v -m unit", "仓库层单元测试"),
        ("pytest tests/utils/ -v -m unit", "工具函数单元测试"),
    ]
    
    for command, description in unit_tests:
        total_tests += 1
        if run_command(command, description):
            success_count += 1
    
    # 2. 集成测试 (中等)
    print("\n🔗 第二层：集成测试 (Integration Tests)")
    print("-" * 30)
    
    integration_tests = [
        ("pytest tests/api/ -v -m integration", "API 集成测试"),
        ("pytest tests/services/ -v -m integration", "服务集成测试"),
    ]
    
    for command, description in integration_tests:
        total_tests += 1
        if run_command(command, description):
            success_count += 1
    
    # 3. 端到端测试 (最少)
    print("\n🎯 第三层：端到端测试 (E2E Tests)")
    print("-" * 30)
    
    e2e_tests = [
        ("pytest tests/e2e/ -v -m e2e", "端到端测试"),
    ]
    
    for command, description in e2e_tests:
        total_tests += 1
        if run_command(command, description):
            success_count += 1
    
    # 4. 覆盖率报告
    print("\n📈 测试覆盖率报告")
    print("-" * 30)
    
    coverage_command = "pytest --cov=corebank --cov-report=html --cov-report=term-missing"
    run_command(coverage_command, "生成覆盖率报告")
    
    # 总结
    print("\n" + "=" * 50)
    print("🏆 测试金字塔执行总结")
    print(f"✅ 成功: {success_count}/{total_tests}")
    print(f"❌ 失败: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️  部分测试失败，请检查上述输出")
        return 1


if __name__ == "__main__":
    sys.exit(main())
