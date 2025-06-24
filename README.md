# 数脉银行 (DataVein Bank) - 安全银行系统

数脉银行是一个使用现代技术构建的全面、安全的银行系统。它提供了强大的后端 API 和用户友好的前端界面，用于核心银行业务操作。

## 🏗️ 系统架构

### 后端 (FastAPI + PostgreSQL)
- **框架**: FastAPI with Python 3.11+
- **数据库**: PostgreSQL 16 with ACID 事务
- **认证**: 基于 JWT 的身份验证
- **安全**: bcrypt 密码哈希，输入验证
- **架构**: 清洁架构，服务/仓库模式
- **容器化**: Podman/Docker 多阶段构建

### 前端 (React + TypeScript)
- **框架**: React 18 with TypeScript
- **构建工具**: Vite 快速开发
- **样式**: Tailwind CSS 现代 UI
- **状态管理**: TanStack Query 服务器状态
- **路由**: React Router 客户端导航
- **表单**: React Hook Form 表单验证
- **测试**: Vitest + Testing Library 测试金字塔

## 🚀 功能特性

### 核心银行业务
- ✅ 用户注册和身份验证
- ✅ 账户管理（支票/储蓄账户）
- ✅ 安全交易（存款、取款、转账）
- ✅ 交易历史和报告
- ✅ 实时余额更新

### 安全特性
- 🔐 基于 JWT 的身份验证
- 🔒 bcrypt 密码哈希
- 🛡️ 输入验证和清理
- 🔍 SQL 注入防护
- 🚫 CORS 保护
- 📝 全面审计日志

### 技术特性
- 🐳 Podman/Docker 完全容器化
- 🗄️ Alembic 数据库迁移
- 🧪 全面测试策略（测试金字塔）
- 📊 健康监控端点
- 🔄 自动数据库连接池
- 📱 响应式 Web 界面

## 📁 项目结构

```
bank/
├── corebank-backend/          # FastAPI 后端
│   ├── corebank/             # 主 Python 包
│   │   ├── api/              # API 端点
│   │   ├── core/             # 配置和数据库
│   │   ├── models/           # Pydantic 模型
│   │   ├── services/         # 业务逻辑
│   │   ├── repositories/     # 数据访问层
│   │   └── security/         # 认证和安全
│   ├── tests/                # 测试套件
│   ├── alembic/              # 数据库迁移
│   ├── compose.yml           # 开发环境
│   └── Containerfile         # 后端容器
├── corebank-frontend/         # React 前端
│   ├── src/                  # 源代码
│   │   ├── components/       # React 组件
│   │   │   └── common/       # 通用组件（采用并置测试）
│   │   │       └── LoadingSpinner/
│   │   │           ├── LoadingSpinner.tsx
│   │   │           ├── index.ts
│   │   │           └── __tests__/
│   │   │               └── LoadingSpinner.test.tsx
│   │   ├── pages/            # 页面组件（采用并置测试）
│   │   │   └── LoginPage/
│   │   │       ├── LoginPage.tsx
│   │   │       ├── index.ts
│   │   │       └── __tests__/
│   │   │           └── LoginPage.test.tsx
│   │   ├── utils/            # 工具函数（采用并置测试）
│   │   │   ├── format.ts
│   │   │   └── __tests__/
│   │   │       └── format.test.ts
│   │   ├── hooks/            # 自定义 hooks
│   │   ├── api/              # API 客户端
│   │   ├── types/            # TypeScript 类型
│   │   └── test/             # 测试配置和工具
│   │       ├── setup.ts      # 全局测试设置
│   │       ├── utils.tsx     # 测试工具函数
│   │       └── vitest.d.ts   # 类型声明
│   ├── Containerfile         # 前端容器
│   ├── nginx.conf            # 生产 Web 服务器
│   └── vitest-setup.d.ts     # Vitest 类型声明
└── reference-AIGraphX/        # 参考实现（AIGraphX 项目）
```

## 🛠️ 快速开始

### 前置要求
- Podman 或 Docker
- Podman Compose 或 Docker Compose
- Node.js 18+ (本地前端开发)
- Python 3.11+ (本地后端开发)

### 开发环境设置

1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd bank
   ```

2. **设置环境变量**
   ```bash
   cd corebank-backend
   cp .env.example .env
   # 编辑 .env 文件配置
   ```

3. **启动开发环境**
   ```bash
   podman-compose up -d
   ```

4. **访问应用**
   - 前端: http://localhost:3000
   - 后端 API: http://localhost:8000
   - API 文档: http://localhost:8000/docs

### 生产部署

1. **使用容器构建和部署**
   ```bash
   podman-compose -f compose.yml up -d
   ```

2. **运行数据库迁移**
   ```bash
   podman exec corebank_app alembic upgrade head
   ```

## 🧪 测试

### 后端测试
```bash
cd corebank-backend
pytest tests/ -v --cov=corebank
```

### 前端测试（测试金字塔）
```bash
cd corebank-frontend
npm test                    # 运行所有测试
npm run test:watch         # 监视模式
npm run test:coverage      # 生成覆盖率报告
npm run type-check         # TypeScript 类型检查
```

#### 前端测试结构
- **单元测试**: 工具函数、组件逻辑 (9个测试)
- **组件测试**: React 组件渲染和交互 (4个测试)
- **集成测试**: 页面级别的用户交互流程 (6个测试)
- **总计**: 19个测试，采用现代并置测试目录结构

## 📚 API 文档

后端提供全面的 API 文档：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要端点
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/accounts` - 列出用户账户
- `POST /api/v1/accounts` - 创建新账户
- `POST /api/v1/transactions/deposit` - 存款
- `POST /api/v1/transactions/withdraw` - 取款
- `POST /api/v1/transactions/transfer` - 账户间转账

## 🔧 配置

### 后端配置
`.env` 文件中的关键环境变量：
- `SECRET_KEY` - JWT 签名密钥
- `DATABASE_URL` - PostgreSQL 连接字符串
- `LOG_LEVEL` - 日志级别 (DEBUG, INFO, WARNING, ERROR)

### 前端配置
- API 基础 URL 在 `vite.config.ts` 中配置
- Vite 配置中的开发代理设置
- 包含生产构建优化

## 🏦 业务规则

### 账户管理
- 每个用户最多 5 个账户
- 每个用户只能有一个储蓄账户
- 最低余额：¥0.00（不允许透支）

### 交易限制
- 最小交易金额：¥0.01
- 每日最大取款：¥10,000
- 单次最大转账：¥50,000

### 安全策略
- 密码要求：8+ 字符，大小写混合，数字
- JWT 令牌过期：30 分钟（可配置）
- 失败登录尝试日志记录

## 🧪 测试策略

### 测试金字塔实现
本项目采用现代前端测试最佳实践：

```
        🎯 集成测试 (6个)
       /                \
      /  页面级用户交互测试  \
     /                      \
    /     单元测试 (13个)      \
   /__________________________\
   工具函数(9) + 组件测试(4)
```

### 测试目录结构
- **并置模式**: 测试文件与源代码并置在 `__tests__` 目录中
- **类型安全**: 完整的 TypeScript 和 jest-dom 类型支持
- **现代工具**: Vitest + Testing Library + 用户事件模拟

## 🤝 贡献

1. Fork 仓库
2. 创建功能分支
3. 进行更改
4. 为新功能添加测试
5. 确保所有测试通过
6. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。

## 🙏 致谢

- 参考 AIGraphX 项目架构构建
- 遵循银行业安全最佳实践
- 实现清洁架构原则
- 使用现代 Web 开发标准
- 采用测试金字塔策略确保代码质量
