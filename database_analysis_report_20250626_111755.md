# 数脉银行数据库结构分析报告
生成时间: 2025-06-26 11:17:55

## 📊 数据库概览
- 总表数: 11
- 总字段数: 111
- 总索引数: 66
- 总记录数: 219

## 📋 表结构详情
### accounts
- 记录数: 9
- 存储大小: 88 kB
- 字段数: 7
- 索引数: 5

#### 字段信息
| 字段名 | 类型 | 可空 | 默认值 | 主键 | 外键 |
|--------|------|------|--------|------|------|
| id | uuid | 否 | gen_random_uuid() | ✓ |  |
| account_number | character varying | 否 |  |  |  |
| user_id | uuid | 否 |  |  | →users.id |
| account_type | USER-DEFINED | 否 |  |  |  |
| balance | numeric | 否 | 0.0000 |  |  |
| created_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |
| updated_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |

#### 索引信息
| 索引名 | 字段 | 唯一 | 类型 |
|--------|------|------|------|
| accounts_account_number_key | account_number | ✓ | btree |
| accounts_pkey | id | ✓ | btree |
| idx_accounts_type | account_type |  | btree |
| idx_accounts_updated_at | updated_at |  | btree |
| idx_accounts_user_id | user_id |  | btree |

### alembic_version
- 记录数: 2
- 存储大小: 24 kB
- 字段数: 1
- 索引数: 1

#### 字段信息
| 字段名 | 类型 | 可空 | 默认值 | 主键 | 外键 |
|--------|------|------|--------|------|------|
| version_num | character varying | 否 |  | ✓ |  |

#### 索引信息
| 索引名 | 字段 | 唯一 | 类型 |
|--------|------|------|------|
| alembic_version_pkc | version_num | ✓ | btree |

### investment_holdings
- 记录数: 7
- 存储大小: 152 kB
- 字段数: 15
- 索引数: 9

#### 字段信息
| 字段名 | 类型 | 可空 | 默认值 | 主键 | 外键 |
|--------|------|------|--------|------|------|
| id | uuid | 否 | gen_random_uuid() | ✓ |  |
| user_id | uuid | 否 |  |  | →users.id |
| account_id | uuid | 否 |  |  | →accounts.id |
| product_id | uuid | 否 |  |  | →investment_products.id |
| shares | numeric | 否 | 0 |  |  |
| average_cost | numeric | 否 |  |  |  |
| total_invested | numeric | 否 | 0 |  |  |
| current_value | numeric | 否 | 0 |  |  |
| unrealized_gain_loss | numeric | 否 | 0 |  |  |
| realized_gain_loss | numeric | 否 | 0 |  |  |
| purchase_date | timestamp with time zone | 否 |  |  |  |
| maturity_date | timestamp with time zone | 是 |  |  |  |
| status | USER-DEFINED | 否 | 'active'::holding_st... |  |  |
| created_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |
| updated_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |

#### 索引信息
| 索引名 | 字段 | 唯一 | 类型 |
|--------|------|------|------|
| idx_investment_holdings_account | account_id |  | btree |
| idx_investment_holdings_maturity | maturity_date |  | btree |
| idx_investment_holdings_product | product_id |  | btree |
| idx_investment_holdings_product_status | product_id, status |  | btree |
| idx_investment_holdings_status | status |  | btree |
| idx_investment_holdings_user | user_id |  | btree |
| idx_investment_holdings_user_status | user_id, status |  | btree |
| investment_holdings_pkey | id | ✓ | btree |
| uq_user_account_product_purchase | user_id, account_id, product_id, purchase_date | ✓ | btree |

### investment_products
- 记录数: 6
- 存储大小: 144 kB
- 字段数: 14
- 索引数: 8

#### 字段信息
| 字段名 | 类型 | 可空 | 默认值 | 主键 | 外键 |
|--------|------|------|--------|------|------|
| id | uuid | 否 | gen_random_uuid() | ✓ |  |
| product_code | character varying | 否 |  |  |  |
| name | character varying | 否 |  |  |  |
| product_type | USER-DEFINED | 否 |  |  |  |
| risk_level | integer | 否 |  |  |  |
| expected_return_rate | numeric | 是 |  |  |  |
| min_investment_amount | numeric | 否 | 1.0000 |  |  |
| max_investment_amount | numeric | 是 |  |  |  |
| investment_period_days | integer | 是 |  |  |  |
| is_active | boolean | 否 | true |  |  |
| description | text | 是 |  |  |  |
| features | jsonb | 是 |  |  |  |
| created_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |
| updated_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |

#### 索引信息
| 索引名 | 字段 | 唯一 | 类型 |
|--------|------|------|------|
| idx_investment_products_active | is_active |  | btree |
| idx_investment_products_active_type | product_type, is_active |  | btree |
| idx_investment_products_code | product_code |  | btree |
| idx_investment_products_risk | risk_level |  | btree |
| idx_investment_products_type | product_type |  | btree |
| idx_investment_products_type_risk | product_type, risk_level |  | btree |
| investment_products_pkey | id | ✓ | btree |
| investment_products_product_code_key | product_code | ✓ | btree |

### investment_transactions
- 记录数: 13
- 存储大小: 208 kB
- 字段数: 16
- 索引数: 12

#### 字段信息
| 字段名 | 类型 | 可空 | 默认值 | 主键 | 外键 |
|--------|------|------|--------|------|------|
| id | uuid | 否 | gen_random_uuid() | ✓ |  |
| user_id | uuid | 否 |  |  | →users.id |
| account_id | uuid | 否 |  |  | →accounts.id |
| product_id | uuid | 否 |  |  | →investment_products.id |
| holding_id | uuid | 是 |  |  | →investment_holdings.id |
| transaction_type | USER-DEFINED | 否 |  |  |  |
| shares | numeric | 否 |  |  |  |
| unit_price | numeric | 否 |  |  |  |
| amount | numeric | 否 |  |  |  |
| fee | numeric | 否 | 0 |  |  |
| net_amount | numeric | 否 |  |  |  |
| status | USER-DEFINED | 否 | 'pending'::investmen... |  |  |
| settlement_date | timestamp with time zone | 是 |  |  |  |
| description | text | 是 |  |  |  |
| created_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |
| updated_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |

#### 索引信息
| 索引名 | 字段 | 唯一 | 类型 |
|--------|------|------|------|
| idx_investment_transactions_account | account_id |  | btree |
| idx_investment_transactions_date | created_at |  | btree |
| idx_investment_transactions_holding | holding_id |  | btree |
| idx_investment_transactions_product | product_id |  | btree |
| idx_investment_transactions_product_type | product_id, transaction_type |  | btree |
| idx_investment_transactions_settlement | settlement_date |  | btree |
| idx_investment_transactions_status | status |  | btree |
| idx_investment_transactions_status_date | status, created_at |  | btree |
| idx_investment_transactions_type | transaction_type |  | btree |
| idx_investment_transactions_user | user_id |  | btree |
| idx_investment_transactions_user_type | user_id, transaction_type |  | btree |
| investment_transactions_pkey | id | ✓ | btree |

### product_nav_history
- 记录数: 93
- 存储大小: 168 kB
- 字段数: 8
- 索引数: 6

#### 字段信息
| 字段名 | 类型 | 可空 | 默认值 | 主键 | 外键 |
|--------|------|------|--------|------|------|
| id | uuid | 否 | gen_random_uuid() | ✓ |  |
| product_id | uuid | 否 |  |  | →investment_products.id |
| nav_date | date | 否 |  |  |  |
| unit_nav | numeric | 否 |  |  |  |
| accumulated_nav | numeric | 是 |  |  |  |
| daily_return_rate | numeric | 是 |  |  |  |
| created_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |
| updated_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |

#### 索引信息
| 索引名 | 字段 | 唯一 | 类型 |
|--------|------|------|------|
| idx_product_nav_history_date | nav_date |  | btree |
| idx_product_nav_history_product | product_id |  | btree |
| idx_product_nav_history_product_date | product_id, nav_date |  | btree |
| idx_product_nav_history_updated_at | updated_at |  | btree |
| product_nav_history_pkey | id | ✓ | btree |
| uq_product_nav_date | product_id, nav_date | ✓ | btree |

### transaction_entries
- 记录数: 50
- 存储大小: 96 kB
- 字段数: 9
- 索引数: 5

#### 字段信息
| 字段名 | 类型 | 可空 | 默认值 | 主键 | 外键 |
|--------|------|------|--------|------|------|
| id | uuid | 否 | gen_random_uuid() | ✓ |  |
| transaction_group_id | uuid | 否 |  |  | →transaction_groups.id |
| account_id | uuid | 否 |  |  | →accounts.id |
| entry_type | USER-DEFINED | 否 |  |  |  |
| amount | numeric | 否 |  |  |  |
| balance_after | numeric | 是 |  |  |  |
| description | text | 是 |  |  |  |
| created_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |
| updated_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |

#### 索引信息
| 索引名 | 字段 | 唯一 | 类型 |
|--------|------|------|------|
| idx_transaction_entries_account | account_id |  | btree |
| idx_transaction_entries_account_created | account_id, created_at |  | btree |
| idx_transaction_entries_group | transaction_group_id |  | btree |
| idx_transaction_entries_type | entry_type |  | btree |
| transaction_entries_pkey | id | ✓ | btree |

### transaction_groups
- 记录数: 25
- 存储大小: 96 kB
- 字段数: 8
- 索引数: 5

#### 字段信息
| 字段名 | 类型 | 可空 | 默认值 | 主键 | 外键 |
|--------|------|------|--------|------|------|
| id | uuid | 否 | gen_random_uuid() | ✓ |  |
| group_type | character varying | 否 |  |  |  |
| description | text | 是 |  |  |  |
| total_amount | numeric | 否 |  |  |  |
| status | USER-DEFINED | 否 | 'pending'::transacti... |  |  |
| reference_id | uuid | 是 |  |  |  |
| created_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |
| updated_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |

#### 索引信息
| 索引名 | 字段 | 唯一 | 类型 |
|--------|------|------|------|
| idx_transaction_groups_created_at | created_at |  | btree |
| idx_transaction_groups_reference | reference_id |  | btree |
| idx_transaction_groups_status | status |  | btree |
| idx_transaction_groups_type | group_type |  | btree |
| transaction_groups_pkey | id | ✓ | btree |

### user_profiles
- 记录数: 2
- 存储大小: 112 kB
- 字段数: 16
- 索引数: 6

#### 字段信息
| 字段名 | 类型 | 可空 | 默认值 | 主键 | 外键 |
|--------|------|------|--------|------|------|
| id | uuid | 否 | gen_random_uuid() | ✓ |  |
| user_id | uuid | 否 |  |  | →users.id |
| real_name | character varying | 是 |  |  |  |
| english_name | character varying | 是 |  |  |  |
| id_type | character varying | 是 |  |  |  |
| id_number | character varying | 是 |  |  |  |
| country | character varying | 是 |  |  |  |
| ethnicity | character varying | 是 |  |  |  |
| gender | character varying | 是 |  |  |  |
| birth_date | date | 是 |  |  |  |
| birth_place | character varying | 是 |  |  |  |
| phone | character varying | 是 |  |  |  |
| email | character varying | 是 |  |  |  |
| address | character varying | 是 |  |  |  |
| created_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |
| updated_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |

#### 索引信息
| 索引名 | 字段 | 唯一 | 类型 |
|--------|------|------|------|
| idx_user_profiles_email | email |  | btree |
| idx_user_profiles_id_number | id_number |  | btree |
| idx_user_profiles_phone | phone |  | btree |
| idx_user_profiles_real_name | real_name |  | btree |
| user_profiles_pkey | id | ✓ | btree |
| user_profiles_user_id_key | user_id | ✓ | btree |

### user_risk_assessments
- 记录数: 3
- 存储大小: 96 kB
- 字段数: 11
- 索引数: 5

#### 字段信息
| 字段名 | 类型 | 可空 | 默认值 | 主键 | 外键 |
|--------|------|------|--------|------|------|
| id | uuid | 否 | gen_random_uuid() | ✓ |  |
| user_id | uuid | 否 |  |  | →users.id |
| risk_tolerance | integer | 否 |  |  |  |
| investment_experience | USER-DEFINED | 否 |  |  |  |
| investment_goal | USER-DEFINED | 否 |  |  |  |
| investment_horizon | USER-DEFINED | 否 |  |  |  |
| monthly_income_range | character varying | 是 |  |  |  |
| assessment_score | integer | 否 |  |  |  |
| assessment_data | jsonb | 是 |  |  |  |
| expires_at | timestamp with time zone | 否 |  |  |  |
| created_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |

#### 索引信息
| 索引名 | 字段 | 唯一 | 类型 |
|--------|------|------|------|
| idx_user_risk_assessments_expires | expires_at |  | btree |
| idx_user_risk_assessments_user | user_id |  | btree |
| idx_user_risk_assessments_user_expires | user_id, expires_at |  | btree |
| uq_user_assessment_date | user_id, created_at | ✓ | btree |
| user_risk_assessments_pkey | id | ✓ | btree |

### users
- 记录数: 9
- 存储大小: 80 kB
- 字段数: 6
- 索引数: 4

#### 字段信息
| 字段名 | 类型 | 可空 | 默认值 | 主键 | 外键 |
|--------|------|------|--------|------|------|
| id | uuid | 否 | gen_random_uuid() | ✓ |  |
| username | character varying | 否 |  |  |  |
| hashed_password | character varying | 否 |  |  |  |
| created_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |
| updated_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |  |
| role | USER-DEFINED | 否 | 'user'::user_role |  |  |

#### 索引信息
| 索引名 | 字段 | 唯一 | 类型 |
|--------|------|------|------|
| idx_users_role | role |  | btree |
| idx_users_updated_at | updated_at |  | btree |
| users_pkey | id | ✓ | btree |
| users_username_key | username | ✓ | btree |

## 🔍 设计分析
### ✅ 设计优点
- 表 accounts 使用UUID主键，有利于分布式系统
- 表 accounts 包含创建和更新时间戳
- 表 investment_holdings 使用UUID主键，有利于分布式系统
- 表 investment_holdings 包含创建和更新时间戳
- 表 investment_products 使用UUID主键，有利于分布式系统
- 表 investment_products 包含创建和更新时间戳
- 表 investment_transactions 使用UUID主键，有利于分布式系统
- 表 investment_transactions 包含创建和更新时间戳
- 表 product_nav_history 使用UUID主键，有利于分布式系统
- 表 product_nav_history 包含创建和更新时间戳
- 表 transaction_entries 使用UUID主键，有利于分布式系统
- 表 transaction_entries 包含创建和更新时间戳
- 表 transaction_groups 使用UUID主键，有利于分布式系统
- 表 transaction_groups 包含创建和更新时间戳
- 表 user_profiles 使用UUID主键，有利于分布式系统
- 表 user_profiles 包含创建和更新时间戳
- 表 user_risk_assessments 使用UUID主键，有利于分布式系统
- 表 user_risk_assessments 包含创建和更新时间戳
- 表 users 使用UUID主键，有利于分布式系统
- 表 users 包含创建和更新时间戳
- 表 users 被 5 个表引用，关系设计良好
- 表 accounts 被 3 个表引用，关系设计良好
- 表 investment_products 被 3 个表引用，关系设计良好
- 表 investment_holdings 被 1 个表引用，关系设计良好
- 表 transaction_groups 被 1 个表引用，关系设计良好

### ⚠️ 发现问题
- 表 alembic_version 缺少时间戳字段

### 💡 优化建议
- 表 ['alembic_version'] 没有外键关系，请确认是否需要建立关联
