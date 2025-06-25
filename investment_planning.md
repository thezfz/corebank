# 投资理财模块设计文档

## 📊 数据库模型设计

### 1. 理财产品表 (investment_products)
```sql
CREATE TABLE investment_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    product_type VARCHAR(50) NOT NULL, -- 'money_fund', 'fixed_term', 'mutual_fund', 'insurance'
    risk_level INTEGER NOT NULL CHECK (risk_level BETWEEN 1 AND 5), -- 1=极低风险, 5=高风险
    expected_return_rate DECIMAL(5,4), -- 预期年化收益率
    min_investment_amount DECIMAL(19,4) NOT NULL DEFAULT 1.00,
    max_investment_amount DECIMAL(19,4),
    investment_period_days INTEGER, -- NULL表示活期
    is_active BOOLEAN NOT NULL DEFAULT true,
    description TEXT,
    features JSONB, -- 产品特色功能
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_investment_products_type ON investment_products(product_type);
CREATE INDEX idx_investment_products_risk ON investment_products(risk_level);
CREATE INDEX idx_investment_products_active ON investment_products(is_active);
```

### 2. 用户风险评估表 (user_risk_assessments)
```sql
CREATE TABLE user_risk_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    risk_tolerance INTEGER NOT NULL CHECK (risk_tolerance BETWEEN 1 AND 5),
    investment_experience VARCHAR(50) NOT NULL, -- 'beginner', 'intermediate', 'advanced'
    investment_goal VARCHAR(100) NOT NULL, -- 'wealth_preservation', 'steady_growth', 'aggressive_growth'
    investment_horizon VARCHAR(50) NOT NULL, -- 'short_term', 'medium_term', 'long_term'
    monthly_income_range VARCHAR(50),
    assessment_score INTEGER NOT NULL,
    assessment_data JSONB, -- 详细评估问卷数据
    expires_at TIMESTAMPTZ NOT NULL, -- 风险评估有效期
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(user_id, created_at)
);

CREATE INDEX idx_user_risk_assessments_user ON user_risk_assessments(user_id);
CREATE INDEX idx_user_risk_assessments_expires ON user_risk_assessments(expires_at);
```

### 3. 投资持仓表 (investment_holdings)
```sql
CREATE TABLE investment_holdings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES investment_products(id),
    shares DECIMAL(19,8) NOT NULL DEFAULT 0, -- 持有份额
    average_cost DECIMAL(19,4) NOT NULL, -- 平均成本
    total_invested DECIMAL(19,4) NOT NULL DEFAULT 0, -- 累计投入
    current_value DECIMAL(19,4) NOT NULL DEFAULT 0, -- 当前市值
    unrealized_gain_loss DECIMAL(19,4) NOT NULL DEFAULT 0, -- 浮动盈亏
    realized_gain_loss DECIMAL(19,4) NOT NULL DEFAULT 0, -- 已实现盈亏
    purchase_date TIMESTAMPTZ NOT NULL,
    maturity_date TIMESTAMPTZ, -- 到期日期（定期产品）
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- 'active', 'matured', 'redeemed'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(user_id, account_id, product_id, purchase_date)
);

CREATE INDEX idx_investment_holdings_user ON investment_holdings(user_id);
CREATE INDEX idx_investment_holdings_account ON investment_holdings(account_id);
CREATE INDEX idx_investment_holdings_product ON investment_holdings(product_id);
CREATE INDEX idx_investment_holdings_status ON investment_holdings(status);
```

### 4. 投资交易表 (investment_transactions)
```sql
CREATE TABLE investment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES investment_products(id),
    holding_id UUID REFERENCES investment_holdings(id),
    transaction_type VARCHAR(50) NOT NULL, -- 'purchase', 'redemption', 'dividend', 'interest'
    shares DECIMAL(19,8) NOT NULL, -- 交易份额
    unit_price DECIMAL(19,4) NOT NULL, -- 单位净值/价格
    amount DECIMAL(19,4) NOT NULL, -- 交易金额
    fee DECIMAL(19,4) NOT NULL DEFAULT 0, -- 手续费
    net_amount DECIMAL(19,4) NOT NULL, -- 净交易金额
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'confirmed', 'failed', 'cancelled'
    settlement_date TIMESTAMPTZ, -- 结算日期
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_investment_transactions_user ON investment_transactions(user_id);
CREATE INDEX idx_investment_transactions_account ON investment_transactions(account_id);
CREATE INDEX idx_investment_transactions_product ON investment_transactions(product_id);
CREATE INDEX idx_investment_transactions_type ON investment_transactions(transaction_type);
CREATE INDEX idx_investment_transactions_status ON investment_transactions(status);
CREATE INDEX idx_investment_transactions_date ON investment_transactions(created_at);
```

### 5. 产品净值历史表 (product_nav_history)
```sql
CREATE TABLE product_nav_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES investment_products(id) ON DELETE CASCADE,
    nav_date DATE NOT NULL, -- 净值日期
    unit_nav DECIMAL(19,4) NOT NULL, -- 单位净值
    accumulated_nav DECIMAL(19,4), -- 累计净值
    daily_return_rate DECIMAL(8,6), -- 日收益率
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(product_id, nav_date)
);

CREATE INDEX idx_product_nav_history_product ON product_nav_history(product_id);
CREATE INDEX idx_product_nav_history_date ON product_nav_history(nav_date);
```

## 🔧 后端API设计

### 1. 理财产品相关API

#### GET /api/v1/investments/products
- 获取理财产品列表
- 支持按类型、风险等级筛选
- 支持分页

#### GET /api/v1/investments/products/{product_id}
- 获取单个产品详情
- 包含历史净值数据

#### GET /api/v1/investments/products/{product_id}/nav-history
- 获取产品净值历史
- 支持时间范围筛选

### 2. 风险评估相关API

#### POST /api/v1/investments/risk-assessment
- 提交风险评估问卷
- 计算风险承受能力

#### GET /api/v1/investments/risk-assessment
- 获取用户当前风险评估结果

#### GET /api/v1/investments/recommendations
- 基于风险评估获取产品推荐

### 3. 投资交易相关API

#### POST /api/v1/investments/purchase
- 购买理财产品
- 扣除账户资金，创建持仓

#### POST /api/v1/investments/redeem
- 赎回理财产品
- 计算收益，返还资金

#### GET /api/v1/investments/holdings
- 获取用户投资持仓
- 包含实时收益计算

#### GET /api/v1/investments/transactions
- 获取投资交易记录
- 支持分页和筛选

### 4. 收益分析相关API

#### GET /api/v1/investments/portfolio-summary
- 获取投资组合总览
- 总资产、总收益、资产配置

#### GET /api/v1/investments/performance
- 获取投资业绩分析
- 收益曲线、风险指标

## 🎨 前端界面设计

### 1. 页面结构
```
/investments
├── /dashboard          # 投资总览
├── /products          # 理财产品
├── /holdings          # 我的持仓
├── /transactions      # 交易记录
├── /risk-assessment   # 风险评估
└── /performance       # 业绩分析
```

### 2. 核心组件设计

#### InvestmentDashboard
- 投资总览卡片
- 资产配置饼图
- 收益趋势图表
- 快速操作入口

#### ProductList
- 产品筛选器
- 产品卡片列表
- 风险等级标识
- 收益率展示

#### HoldingsList
- 持仓产品列表
- 实时盈亏显示
- 操作按钮（赎回）
- 收益详情

#### TransactionHistory
- 交易记录表格
- 状态筛选
- 分页控制
- 交易详情模态框

#### RiskAssessment
- 问卷表单
- 进度指示器
- 结果展示
- 产品推荐

### 3. 数据可视化
- Chart.js / Recharts 图表库
- 收益曲线图
- 资产配置饼图
- 风险收益散点图
- 净值走势图

## 🔒 安全考虑

### 1. 交易安全
- 交易密码验证
- 交易限额控制
- 异常交易监控
- 交易确认机制

### 2. 数据安全
- 敏感数据加密
- API访问控制
- 审计日志记录
- 数据备份策略

### 3. 风险控制
- 投资适当性检查
- 风险提示展示
- 冷静期机制
- 投资者教育

## 📊 业务规则

### 1. 投资限制
- 单个产品最大投资比例
- 高风险产品投资门槛
- 风险等级匹配检查
- 投资冷静期

### 2. 收益计算
- 实时净值更新
- 复利计算
- 费用扣除
- 税收处理

### 3. 赎回规则
- 赎回手续费
- 赎回到账时间
- 部分赎回支持
- 强制赎回条件

## 🧪 测试策略

### 1. 单元测试
- 收益计算逻辑
- 风险评估算法
- 数据验证规则
- 业务规则检查

### 2. 集成测试
- API端点测试
- 数据库事务测试
- 第三方服务集成
- 异常场景处理

### 3. 性能测试
- 大量数据查询
- 并发交易处理
- 实时计算性能
- 缓存策略验证

## 🚀 实施计划

### Phase 1: 基础功能 (2-3周)
- 数据库模型创建
- 基础API开发
- 产品管理功能
- 简单投资交易

### Phase 2: 核心功能 (3-4周)
- 风险评估系统
- 持仓管理
- 收益计算
- 前端界面开发

### Phase 3: 高级功能 (2-3周)
- 数据可视化
- 投资建议
- 性能优化
- 安全加固

### Phase 4: 测试与优化 (1-2周)
- 全面测试
- 性能调优
- 用户体验优化
- 文档完善
