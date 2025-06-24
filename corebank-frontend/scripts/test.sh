#!/bin/bash

echo "🏆 CoreBank 前端测试金字塔执行"
echo "=================================="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

success_count=0
total_tests=0

run_test() {
    local command=$1
    local description=$2
    
    echo -e "\n${BLUE}🔄 $description${NC}"
    echo "执行命令: $command"
    
    if eval $command; then
        echo -e "${GREEN}✅ $description - 成功${NC}"
        ((success_count++))
    else
        echo -e "${RED}❌ $description - 失败${NC}"
    fi
    ((total_tests++))
}

# 1. 单元测试 (最多)
echo -e "\n📊 第一层：单元测试 (Unit Tests)"
echo "------------------------------"

run_test "npm run test -- --run src/utils/" "工具函数单元测试"
run_test "npm run test -- --run src/components/common/" "通用组件单元测试"
run_test "npm run test -- --run src/hooks/" "自定义 Hook 单元测试"

# 2. 集成测试 (中等)
echo -e "\n🔗 第二层：集成测试 (Integration Tests)"
echo "------------------------------"

run_test "npm run test -- --run src/pages/" "页面集成测试"
run_test "npm run test -- --run src/components/layout/" "布局组件集成测试"

# 3. 端到端测试 (最少)
echo -e "\n🎯 第三层：端到端测试 (E2E Tests)"
echo "------------------------------"

run_test "npm run test -- --run src/e2e/" "端到端测试"

# 4. 覆盖率报告
echo -e "\n📈 测试覆盖率报告"
echo "------------------------------"

echo -e "${BLUE}🔄 生成覆盖率报告${NC}"
npm run test:coverage

# 总结
echo -e "\n=================================="
echo "🏆 前端测试金字塔执行总结"
echo -e "✅ 成功: ${GREEN}$success_count${NC}/$total_tests"
echo -e "❌ 失败: ${RED}$((total_tests - success_count))${NC}/$total_tests"

if [ $success_count -eq $total_tests ]; then
    echo -e "${GREEN}🎉 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}⚠️  部分测试失败，请检查上述输出${NC}"
    exit 1
fi
