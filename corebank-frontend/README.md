#### **数脉银行 Frontend - 用户界面设计与实现 v2.0**

**1. 引言与指导原则**

本文档为数脉银行前端 UI 提供了完整的设计与实现规划，旨在为后端 API 提供一个安全、直观且高效的用户界面。

-   **简洁与清晰:** 界面设计必须清晰、无歧义。用户执行的每一项操作（如转账）都应有明确的提示和二次确认。
-   **安全第一:** 所有用户输入都必须经过前端验证。密码等敏感信息在传输和显示上必须遵循安全最佳实践（例如，绝不存储明文密码，输入时使用掩码）。
-   **用户体验优先:** 提供即时、准确的反馈，包括操作成功、失败原因、加载状态等。
-   **组件化开发:** 构建可复用的 UI 组件（如账户卡片、交易列表项、表单输入框），提高开发效率和一致性。
-   **测试驱动开发:** 采用测试金字塔策略，确保代码质量和可维护性。
-   **环境一致性:** **必须**使用 **Podman Compose** 统一管理开发环境，确保前端开发服务器与后端 API 的连接稳定一致。

**2. 核心需求 (Frontend MVP)**

-   **认证页面:**
    -   提供登录表单（用户名、密码）。
    -   提供注册表单（用户名、密码、确认密码）。
    -   处理登录成功后的 Token 存储（如 `localStorage` 或 `sessionStorage`）和路由跳转。
-   **主面板 (Dashboard):**
    -   用户登录后看到的第一个页面。
    -   以卡片形式清晰展示用户拥有的所有账户（储蓄账户、支票账户）及其当前余额。
    -   提供醒目的按钮或链接以发起“存款”、“取款”、“转账”等核心操作。
-   **交易页面:**
    -   **表单驱动:** 提供清晰的表单来执行交易：
        -   **存款/取款:** 选择账户，输入金额。
        -   **转账:** 选择源账户、目标账户（初期仅限用户自己的账户），输入金额，提供备注。
    -   **二次确认:** 所有交易在提交前**必须**有一个模态框（Modal）或确认页面，清晰地展示交易详情（如“您确定要从账户 A 向账户 B 转账 100.00 元吗？”），需要用户再次点击确认。
-   **账户详情页:**
    -   点击主面板的账户卡片后进入。
    -   显示该账户的详细信息。
    -   以列表形式清晰展示该账户的**交易历史记录**，包括交易类型、金额、时间戳等。
-   **全局功能:**
    -   受保护的路由：未登录用户无法访问除登录/注册外的任何页面。
    *   提供“登出”功能，清除本地存储的 Token 并跳转到登录页。

**3. 技术选型与架构**

我们将采用与您之前项目类似的、成熟且高效的技术栈。

| 类别              | 推荐技术                   | 理由                                                           |
| :---------------- | :------------------------- | :------------------------------------------------------------- |
| **核心框架**      | **React (v18+)**           | 社区成熟，生态强大，适合构建数据驱动的 UI。                    |
| **构建工具**      | **Vite**                   | 极快的开发体验和现代化的构建标准。                             |
| **编程语言**      | **TypeScript**             | **强制要求**，为金融应用的健壮性提供类型安全保障。             |
| **路由管理**      | **React Router (v6+)**     | 标准的客户端路由解决方案。                                     |
| **数据请求/状态** | **TanStack Query** | **强烈推荐**，优雅地管理 API 数据获取、缓存和状态同步。    |
| **UI 样式**       | **Tailwind CSS**           | 快速构建一致、定制化的 UI。                                    |
| **UI 组件库**     | **Headless UI / Radix UI** | **推荐**，提供无样式的、功能完备的组件（如下拉菜单、模态框），与 Tailwind CSS 完美结合，确保可访问性。 |
| **表单管理**      | **React Hook Form**        | **推荐**，用于管理复杂的表单状态和验证，性能优秀。             |

**4. 目录结构（已实现）**

采用现代前端最佳实践的 `corebank-frontend/` 目录结构：

```
corebank-frontend/
├── public/
├── src/
│   ├── api/              # API 客户端与 TanStack Query hooks
│   ├── assets/           # 图片、图标等静态资源
│   ├── components/       # 可复用 UI 组件（采用并置测试）
│   │   └── common/       # 通用组件
│   │       └── LoadingSpinner/
│   │           ├── LoadingSpinner.tsx    # 组件实现
│   │           ├── index.ts              # 导出文件
│   │           └── __tests__/            # 并置测试目录
│   │               └── LoadingSpinner.test.tsx
│   ├── pages/            # 页面级组件（采用并置测试）
│   │   ├── LoginPage/
│   │   │   ├── LoginPage.tsx             # 页面实现
│   │   │   ├── index.ts                  # 导出文件
│   │   │   └── __tests__/                # 并置测试目录
│   │   │       └── LoginPage.test.tsx
│   │   └── RegisterPage.tsx              # 其他页面
│   ├── utils/            # 工具函数（采用并置测试）
│   │   ├── format.ts                     # 格式化工具
│   │   └── __tests__/                    # 并置测试目录
│   │       └── format.test.ts
│   ├── hooks/            # 自定义 React Hooks
│   ├── types/            # TypeScript 类型定义
│   └── test/             # 测试配置和工具
│       ├── setup.ts      # 全局测试设置
│       ├── utils.tsx     # 测试工具函数
│       └── vitest.d.ts   # 类型声明文件
├── .env.development      # 开发环境变量
├── .env.production       # 生产环境变量
├── Containerfile         # Podman/Docker 构建文件
├── vitest-setup.d.ts     # Vitest 类型声明
├── vitest.config.ts      # 测试配置
├── package.json
├── tsconfig.json
└── vite.config.ts
```

**5. 测试策略实现（已完成）**

### 测试金字塔架构

本项目成功实现了现代前端测试金字塔：

```
        🎯 集成测试 (6个)
       /                \
      /  LoginPage 页面测试  \
     /                      \
    /     单元测试 (13个)      \
   /__________________________\
   工具函数(9) + 组件测试(4)
```

### 测试类型与覆盖

- **单元测试 (13个)**
  - `format.test.ts`: 货币和日期格式化函数 (9个测试)
  - `LoadingSpinner.test.tsx`: 加载组件渲染测试 (4个测试)

- **集成测试 (6个)**
  - `LoginPage.test.tsx`: 完整的用户登录流程测试
    - 表单渲染和验证
    - 用户交互和状态管理
    - 错误处理和加载状态

### 测试工具链

- **测试框架**: Vitest (快速、现代)
- **测试库**: @testing-library/react (用户行为驱动)
- **用户事件**: @testing-library/user-event (真实用户交互)
- **类型支持**: 完整的 TypeScript 和 jest-dom 类型声明
- **测试结构**: 并置模式 (`__tests__` 目录)

### 运行测试

```bash
npm test                    # 运行所有测试
npm run test:watch         # 监视模式
npm run test:coverage      # 生成覆盖率报告
npm run type-check         # TypeScript 类型检查
```

**6. 结论**

数脉银行前端项目已成功实现：

- ✅ **现代化架构**: 独立前端项目，清晰的代码组织
- ✅ **测试金字塔**: 19个测试覆盖单元、组件、集成层面
- ✅ **并置测试**: 测试文件与源代码并置，便于维护
- ✅ **类型安全**: 完整的 TypeScript 支持
- ✅ **开发体验**: 热重载、类型检查、自动化测试

这为构建一个安全、可靠且用户友好的银行系统界面奠定了坚实的基础。