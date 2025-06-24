### **数脉银行系统 - 独立设计与架构 v2.0**

**1. 引言与指导原则**

本文档为数脉银行 v2.0 项目提供了详尽、独立的架构与设计规范。本方案基于成熟的软件工程最佳实践，旨在构建一个**健壮、可维护且高度可测试的**银行核心系统，并为未来的功能扩展奠定坚实的基础。

方案严格遵循以下指导原则：

-   **简洁至上 ("大道至简"):** 从满足核心银行交易的最简可行产品（MVP）着手。MVP 阶段将**严格排除**贷款、信用卡、投资理财等复杂业务，专注于基础的用户、账户和交易功能。
-   **安全与稳定压倒一切:** 在银行业务场景下，安全性和数据一致性是最高优先级。所有设计都必须将此作为首要考量。
-   **迭代开发:** 构建坚实的交易核心，仅在核心稳固且有明确业务需求时，才逐步引入新功能。
-   **可测试性:** 这是确保银行系统逻辑正确无误的基石。所有组件，尤其是涉及资金计算和流转的服务与仓库，**必须**设计为易于进行集成测试。
-   **显式接口与一致性:** 严格定义并强制执行 API、函数签名、数据模型（特别是与货币/精度相关的）和错误处理规范。这是确保团队协作顺畅、避免模块集成失败的关键。
-   **统一实现模式 (!!!):** **必须**在**依赖注入管理**、**事务管理**和**测试策略**上采用统一、明确的最佳实践模式，避免因逻辑混乱导致的安全漏洞或数据不一致问题。
-   **务实的技术选型:** 使用成熟、稳定且适合金融交易场景的技术。
-   **安全优先:** **绝不**硬编码或在版本控制中存储任何敏感信息（API密钥、数据库密码等）。所有金额处理**必须**使用能避免浮点数精度问题的类型（如 `Decimal`）。
-   **状态管理:** **严禁**使用全局变量管理应用状态，**必须**使用 `app.state` 结合 `lifespan` 进行管理。
-   **环境一致性 (!!!):** **必须**使用容器化技术 (**Podman**) 和编排工具 (**Podman Compose**) 来管理所有服务（应用、数据库），确保开发、测试和部署环境的绝对一致性。

**2. 核心需求 (MVP 范围)**

初始版本将专注于构建一个能够实现以下核心功能的银行系统：

-   **用户管理:**
    -   新用户注册（安全的密码哈希存储）。
    -   用户登录，获取认证 Token (JWT)。
-   **账户管理:**
    -   为已认证用户创建账户（如：储蓄账户、支票账户）。
    -   查询用户拥有的账户列表及其详细信息（如：账号、余额、账户类型）。
-   **核心交易 (原子性):**
    -   存款 (Deposit) 到指定账户。
    -   取款 (Withdraw) 从指定账户（需检查余额）。
    -   转账 (Transfer) 在同一用户自己的两个账户之间进行。
-   **基础查询:**
    -   查询指定账户的交易流水记录。
-   **API 访问:** 提供稳定、安全的 RESTful API 以执行上述所有操作。

**3. 简化架构**

采用**模块化单体**后端服务（FastAPI 应用），数据库选用具备强大事务支持的 PostgreSQL。整个环境通过 Podman Compose 进行管理。

```mermaid
graph TD
    subgraph "客户端 (Web/Mobile App)"
        User[用户] --> |HTTPS/JWT| API
    end

    subgraph "后端服务 (FastAPI 应用 - Podman 容器)"
        API[RESTful API 端点<br>(/auth, /accounts, /transactions)] --> AS[账户服务]
        API --> TS[交易服务]

        subgraph "服务层 (业务逻辑)"
            AS(AccountService<br>- 管理账户生命周期)
            TS(TransactionService<br>- 处理资金流转<br>- 确保事务原子性)
        end

        subgraph "仓库层 (数据访问)"
            PR(PostgresRepository<br>- 封装所有 SQL 操作<br>- 参与事务管理)
        end
    end

    subgraph "数据库 (Podman 容器)"
        PG[(PostgreSQL<br>- 存储用户、账户、交易<br>- 使用事务)]
    end

    API -- 调用 --> AS & TS
    AS & TS -- 使用 --> PR
    PR -- 读写 --> PG

    style PG fill:#D6EAF8,stroke:#333,stroke-width:2px
    style API fill:#FEF9E7,stroke:#333,stroke-width:2px
```

**关键架构决策与简化措施:**

*   **单一后端服务:** FastAPI 应用，内部严格分层（API -> Service -> Repository）。
*   **核心数据库:** **只使用 PostgreSQL**。它的事务支持（ACID）对于保证银行数据的一致性至关重要。
*   **容器化环境 (!!!):** **必须**使用 `compose.yml` (Podman Compose) 统一管理 FastAPI 应用和 PostgreSQL 服务容器。
*   **事务管理:** 业务逻辑层（Service）将负责编排事务边界。仓库层（Repository）的方法将作为可组合的事务单元。
*   **异步后台任务:** MVP 阶段无。未来可用于发送邮件通知、生成月度报表等。
*   **缓存:** MVP 阶段无。未来可使用 Redis 缓存不常变动的账户信息。
*   **基础健康检查:** 提供 `/health` 端点，用于检查服务和数据库连接状态。
*   **配置管理:** 采用环境变量 + `.env` 文件的方式。
*   **数据库模式管理 (!!! 关键 !!!):** **必须**使用 **Alembic** 管理 PostgreSQL 数据库模式的创建和所有后续迁移。

**4. 目录结构 (简化且聚焦)**

```
corebank-backend/
├── corebank/          # 后端服务主 Python 包
│   ├── __init__.py
│   ├── main.py        # FastAPI 应用实例与启动逻辑
│   ├── logging_config.py
│   ├── core/          # 核心工具、配置加载、数据库客户端设置
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── db.py        # 数据库客户端初始化 (PG), lifespan 管理
│   ├── models/        # API Pydantic 模型 (!!! 严格用于 API 边界 !!!)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── account.py
│   │   └── transaction.py
│   ├── schemas/       # (可选) 内部 Pydantic 模型
│   ├── security/      # (推荐) 安全相关逻辑
│   │   ├── __init__.py
│   │   ├── password.py  # 密码哈希与验证
│   │   └── token.py     # JWT Token 生成与解码
│   ├── api/           # FastAPI 路由与端点
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py
│   │       ├── dependencies.py # (!!! 核心依赖提供者 !!!)
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py
│   │           ├── accounts.py
│   │           └── transactions.py
│   ├── services/      # 服务层 (业务逻辑 & 事务管理)
│   │   ├── __init__.py
│   │   ├── account_service.py
│   │   └── transaction_service.py
│   └── repositories/  # 仓库层 (数据访问)
│       ├── __init__.py
│       └── postgres_repo.py
├── tests/             # 测试 (!!! 结构镜像代码 !!!)
│   ├── conftest.py    # Pytest Fixtures
│   ├── api/
│   ├── services/
│   └── repositories/    # (集成测试为主)
├── alembic/           # Alembic 迁移脚本目录
├── docs/
├── logs/
├── .env.example
├── pyproject.toml
├── Containerfile
├── compose.yml
├── compose.test.yml
├── alembic.ini
```

**5. 核心数据模型 (PostgreSQL)**

这是银行系统的核心，将在 Alembic 迁移脚本中精确定义。

*   **`users` 表**
    *   `id`: UUID (Primary Key)
    *   `username`: VARCHAR(255) (Unique, Indexed)
    *   `hashed_password`: VARCHAR(255)
    *   `created_at`: TIMESTAMPTZ
*   **`accounts` 表**
    *   `id`: UUID (Primary Key)
    *   `account_number`: VARCHAR(20) (Unique, Indexed, **系统生成**)
    *   `user_id`: UUID (Foreign Key to `users.id`)
    *   `account_type`: VARCHAR(50) (e.g., 'checking', 'savings')
    *   `balance`: DECIMAL(19, 4) (**必须**使用 `Decimal` 类型，非 `Float`！)
    *   `created_at`: TIMESTAMPTZ
    *   **Constraint:** `CHECK (balance >= 0)`
*   **`transactions` 表**
    *   `id`: UUID (Primary Key)
    *   `account_id`: UUID (Foreign Key to `accounts.id`)
    *   `transaction_type`: VARCHAR(50) (e.g., 'deposit', 'withdrawal', 'transfer')
    *   `amount`: DECIMAL(19, 4)
    *   `related_account_id`: UUID (Nullable, Foreign Key to `accounts.id`, for transfers)
    *   `timestamp`: TIMESTAMPTZ

**6. 关键模块职责与接口**

*   **`corebank/core`**: 应用配置、日志配置、数据库客户端/连接池生命周期管理 (`lifespan`)。
*   **`corebank/models`**: **严格用于 API 边界**的 Pydantic 模型。
*   **`corebank/schemas`**: (可选) 内部业务流程中使用的 Pydantic 模型。
*   **`corebank/api`**: FastAPI 路由、端点**保持轻薄**，主要负责请求验证、调用 `services` 并格式化响应。依赖项**必须**通过 `dependencies.py` 注入。
*   **`corebank/services`**: 包含所有核心业务逻辑，例如“创建账户”、“执行转账”等。**是数据库事务的管理边界**。
*   **`corebank/repositories`**: 数据访问层，封装所有对数据库的交互。其方法应是**无业务逻辑的、可复用的**数据操作单元。
*   **`corebank/security`**: 包含密码哈希、JWT Token 生成与验证等安全关键逻辑。

**7. 严格的 API 设计与接口规范 (!!!关键!!!)**

*   **RESTful 原则:** 遵循标准的 HTTP 方法和资源命名。
*   **一致的命名:**
    *   API 路径: **必须**使用小写复数形式，如 `/v1/accounts`, `/v1/transactions`。
    *   JSON 键 / 查询参数: **必须**使用 `snake_case`，如 `account_id`, `transaction_type`。
*   **标准 HTTP 状态码:**
    *   `200 OK`: 请求成功。
    *   `201 Created`: 资源创建成功。
    *   `204 No Content`: 操作成功但无返回体。
    *   `400 Bad Request`: 客户端请求无效（如验证失败）。
    *   `401 Unauthorized`: 未认证。
    *   `403 Forbidden`: 已认证但无权限。
    *   `404 Not Found`: 资源不存在。
    *   `500 Internal Server Error`: 服务器内部错误。
*   **一致的错误响应格式:** 所有错误 (4xx, 5xx) **必须** 返回统一的 JSON 格式: `{"detail": "A descriptive error message."}`。**必须**通过 FastAPI 的自定义异常处理器统一实现。
*   **Pydantic 用于所有 API 输入/输出:** 请求体验证，响应体使用 `response_model`。**必须**严格执行。
*   **版本控制:** API 路径中**必须**包含版本号，如 `/v1/`。

**8. 严格的函数/方法签名规范与依赖注入 (!!!关键!!!)**

*   **强制类型提示:** 所有函数和方法签名（包括 `__init__`）的参数和返回值**必须**使用 Python 类型提示。
*   **强制 PEP 8 命名规范:** **必须**严格遵守。
*   **静态分析 (`mypy`):** **必须**配置 `mypy` 并作为 CI 流水线的一部分，强制检查类型提示的正确性。
*   **代码格式化与 Linting (`black`, `ruff`):** **必须**使用这些工具并作为 CI 流水线的强制步骤。
*   **强制一致的文档字符串 (Docstrings):** 所有公共模块、类、函数和方法**必须**包含符合 PEP 257 规范的 Docstring。

**8.1 依赖注入 (DI) 策略 (FastAPI 应用)**

*   **集中管理依赖提供者:**
    *   所有 FastAPI 端点和服务的**核心依赖项**（如数据库仓库, 服务本身）的**获取逻辑**，**必须**统一由 **`corebank/api/v1/dependencies.py`** 模块中的**依赖提供函数**（例如 `get_postgres_repository`, `get_account_service`）负责。
    *   **严禁**在其他地方定义并使用**替代的或重复的**依赖提供逻辑。
*   **依赖提供者实现原则:**
    *   直接使用从 `corebank/core/config.py` 加载的配置。
    *   **如果**需要访问由 `lifespan` 管理的共享资源（如连接池），**必须**通过注入 `request: Request` 访问 `request.app.state` 获取，并**健壮地处理**资源不存在的情况。
*   **`lifespan` 的职责:** `corebank/core/db.py` 中的 `lifespan` 管理器应专注于管理**底层共享资源**（如 `psycopg_pool`）的**生命周期**，并将这些资源存储在 **`app.state`** 中。
*   **状态管理:** **再次强调，严禁使用可变的全局变量来存储应用状态**。**必须**通过 FastAPI 的 `app.state` 属性进行管理。

**9. 配置管理**

*   **容器化优先:** 配置应优先考虑在容器化环境中使用环境变量。
*   **本地开发:** 使用根目录下的 `.env` 文件存储敏感信息，供 Podman Compose 或本地直接运行读取。
*   **.gitignore:** **必须**包含 `.env` 和 `logs/`。
*   **.env.example:** **必须**提供，列出所有必需的环境变量及其格式（包括主数据库和测试数据库的配置）。
*   **代码加载:** **必须**在 `corebank/core/config.py` 中**集中一次性**加载配置。**强烈推荐**使用 **Pydantic Settings** (`pydantic-settings` 库) 将配置加载到结构化的类中。

**10. 日志记录策略**

*   **工具:** **必须**使用 Python 内置的 `logging` 模块。
*   **配置:** **必须**在 `corebank/logging_config.py` 中进行集中配置，并在应用启动时调用。
*   **格式:** **必须**包含标准信息：时间戳 (`asctime`)、级别 (`levelname`)、记录器名称 (`name`)、消息 (`message`)。
*   **级别:** **必须**使日志级别可配置 (通过环境变量 `LOG_LEVEL`, 默认 `INFO`)。
*   **输出:** 开发环境输出到控制台，生产环境输出到 `logs/` 目录下的文件。

**11. !!! 重要：API 密钥与敏感信息管理 !!!**

*   **风险:** 硬编码或提交到 Git 会导致严重安全问题。
*   **解决方案:** **必须**遵循第 9 节的配置管理方法（环境变量 + `.env` + `.gitignore`）。

**12. 后台任务与独立脚本**

*   **MVP 阶段无。**
*   **未来规划:** 独立脚本（如 `scripts/generate_monthly_statements.py`）应作为独立的 Python 程序运行，独立加载配置和初始化所需资源，**严禁**依赖 FastAPI 应用实例或 `lifespan`。

**13. 测试策略 (!!! 核心实践 - 前后端测试金字塔 !!!)**

**13.1 基础原则与模型选择**

*   **后端**: 本项目明确采用**受"测试奖杯 (Testing Trophy)"启发的测试策略**，将最大资源投入到集成测试，以获得最高的投资回报率和信心。
*   **前端**: 已成功实现**测试金字塔 (Testing Pyramid)**策略，采用现代前端测试最佳实践，确保代码质量和可维护性。

**13.2 测试环境与数据管理 (!!! 关键 !!!)**

*   **测试环境 (Podman Compose):**
    *   **必须**使用独立的 `compose.test.yml` 文件来定义和启动集成测试所需的 PostgreSQL 容器。
    *   **必须**确保测试 PostgreSQL 服务使用一个**隔离的数据库实例**（例如，通过 `POSTGRES_DB` 环境变量设置为 `test_corebank_pg`）。
*   **资源管理 (Pytest Fixtures in `conftest.py`):**
    *   使用 Fixture 管理测试资源的生命周期（数据库连接池、测试客户端等）。
    *   **模式初始化 (一次性):** 使用 `session` 作用域的 Fixture，在所有测试开始前，确保对测试数据库运行 `alembic upgrade head`，使其模式与最新代码匹配。
*   **数据清理 Fixture (!!! 极其重要 !!!):**
    *   **必须**创建一个 `function` 作用域的、`autouse=True` 的 Fixture。
    *   此 Fixture 在**每个测试函数执行后**，对测试数据库执行 `TRUNCATE users, accounts, transactions RESTART IDENTITY CASCADE;`，彻底清空所有相关表。**这是确保测试间绝对隔离的关键**。
*   **测试数据:** **必须**使用 `factory_boy` (`pytest-factoryboy`) 和 `Faker` 按需生成逼真的测试数据。

**13.3 各层测试策略详解**

| 测试类型     | 主要关注层级                    | 主要职责                                                           | 关键工具/技术                                                | 相对数量 (奖杯形状) |
| :----------- | :------------------------------ | :----------------------------------------------------------------- | :----------------------------------------------------------- | :------------------ |
| 静态分析     | 所有代码层                      | 捕获类型错误、代码风格问题、潜在 Bug                               | Mypy, Ruff                                                   | (基础)              |
| 单元测试     | Utils, Models, Security, Services (纯逻辑) | 验证隔离的、无副作用的代码单元逻辑                                 | Pytest, unittest.mock (AsyncMock), Fake 对象                 | 小                  |
| **集成测试** | **Repositories, Services (事务), API (契约)** | **验证组件协作、与真实测试数据库的交互、API 契约、事务原子性**   | **Pytest, httpx, Podman Compose, Fixtures, factory_boy, `app.dependency_overrides`** | **大 (核心)** |
| 端到端测试   | (可选) 关键业务流程（如完整转账） | 模拟真实用户场景，验证整个系统的协同工作                           | Pytest + httpx (API 驱动)                                    | 极小                |

**13.4 API 端点测试 (主要集成测试 Mock Service)**

*   **工具:** **必须**使用异步测试客户端 `httpx.AsyncClient`。
*   **核心策略:** 在测试 API 端点时，**必须**使用 `app.dependency_overrides` 来 Mock 服务层（Service）的依赖。
*   **测试焦点:** 验证 API 路由、请求体验证、响应序列化、对 Mock Service 的正确调用、HTTP 状态码和认证逻辑。
*   **清理:** **必须**在每个测试后彻底清理 `dependency_overrides`。

**13.5 前端测试金字塔实现 (已完成)**

*   **测试结构**: 采用现代并置测试模式，测试文件与源代码在 `__tests__` 目录中并置
*   **测试工具链**: Vitest + @testing-library/react + @testing-library/user-event
*   **类型安全**: 完整的 TypeScript 和 jest-dom 类型支持
*   **测试覆盖**:
    - 单元测试 (13个): 工具函数和组件逻辑
    - 集成测试 (6个): 页面级用户交互流程
    - 总计 19个测试，覆盖关键业务逻辑

**14. 未来增强功能 (MVP 之后)**

*   明确推迟以下功能：用户间转账、多币种支持、高级报表、欺诈检测、消息队列通知、集中配置服务、高级缓存层。

**15. 部署注意事项**

*   **环境一致性:** **必须**使用与开发/测试环境一致的容器化方式（如 Podman 镜像）进行部署。
*   **配置管理:** **绝不**部署 `.env` 文件。在部署环境通过**平台的环境变量管理机制**设置真实配置。
*   **数据库初始化/迁移:** 在部署流程中**必须**包含运行 `alembic upgrade head` 的步骤，以确保数据库模式与代码版本匹配。
*   **CI/CD 集成:** 部署应作为 CI/CD 流水线的一部分，在所有检查和测试通过后自动触发。

**16. 结论**

这份独立的设计文档为数脉银行系统提供了一份明确、规范且安全的开发蓝图。通过聚焦核心功能、采用容器化的务实架构、强制执行严格的接口与编码规范，并实施前后端完整的测试策略，本项目旨在最大限度地减少开发痛点，构建一个高质量、可信赖的银行系统。

项目的成功不仅依赖于简洁的设计，更依赖于对**统一实现模式、自动化数据库管理 (Alembic) 和经过实践验证的测试策略**的严格遵循。

**已实现的关键成果:**
- ✅ **后端**: 基于测试奖杯的集成测试策略
- ✅ **前端**: 完整的测试金字塔实现 (19个测试)
- ✅ **现代化工具链**: Vitest + Testing Library + TypeScript
- ✅ **并置测试结构**: 便于维护的测试组织方式
- ✅ **类型安全**: 完整的 TypeScript 和 jest-dom 支持

**强烈建议开发者将本文档视为项目开发的"契约"，并严格遵循其中定义的结构、规范和原则**，以确保项目健康、高效地推进。