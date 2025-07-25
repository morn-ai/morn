# Morn Agent

[English](README.md) | 简体中文

## 快速开始

### 前置要求

- Python 3.11 或更高版本
- [uv](https://github.com/astral-sh/uv)（推荐）或 pip

### 安装

#### 使用 uv（推荐）

```bash
# 克隆仓库
git clone https://github.com/morn-ai/morn.git
cd morn

# 安装依赖
uv sync

# 运行开发服务器
uv run python app/app.py
```

#### 使用 pip

```bash
# 克隆仓库
git clone https://github.com/morn-ai/morn.git
cd morn

# 安装依赖
pip install -e .

# 运行开发服务器
python app/app.py
```

## 认证系统

本项目实现了灵活的认证系统，支持两种认证模式：

1. **JWT 模式** (`jwt`): 基于 JWT (JSON Web Token) 的用户认证系统，支持登录获取令牌和 API 访问保护
2. **无认证模式** (`none`): 无需认证，任何人都可以访问 API，适用于开发环境或内部系统

### 配置

在环境变量中设置以下配置：

```bash
# 认证模式 (none | jwt)
# none: 无需认证，任何人都可以访问 API
# jwt: 需要 JWT 认证
MORN_AUTH_MODE=jwt

# 管理员凭据
MORN_ADMIN_USERNAME=admin
MORN_ADMIN_PASSWORD=your_password

# JWT 配置
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120

# 防暴力破解配置
MAX_FAILED_ATTEMPTS=5
LOCKOUT_DURATION=300
MAX_ATTEMPTS_PER_MINUTE=10
FAILED_ATTEMPT_DELAY=2
```

### API 端点

#### 1. 用户登录

**POST** `/login`

请求体：
```json
{
  "username": "admin",
  "password": "your_password"
}
```

响应：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 7200
}
```

#### 2. 获取当前用户信息

**GET** `/me`

需要在请求头中包含 Bearer Token：
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

响应：
```json
{
  "username": "admin"
}
```

#### 3. 受保护的 API

所有需要认证的 API 都需要在请求头中包含 Bearer Token。

例如，聊天 API：
**POST** `/api/v1/chat/completions`

请求头：
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### 认证模式说明

#### JWT 模式 (默认)
- 设置 `MORN_AUTH_MODE=jwt`
- 所有 API 都需要有效的 JWT 令牌
- 用户必须先登录获取令牌
- 适用于生产环境

#### 无认证模式
- 设置 `MORN_AUTH_MODE=none`
- 所有 API 都可以直接访问，无需令牌
- 登录 API 会接受任何用户名和密码
- 适用于开发环境或内部系统

### 在代码中使用

#### 保护路由

在需要认证的路由中添加依赖：

```python
from app.api.auth import require_auth
from app.schemas.auth import TokenData
from typing import Annotated
from fastapi import Depends

@router.post("/protected-endpoint")
async def protected_endpoint(
    current_user: Annotated[TokenData, Depends(require_auth)]
):
    # 只有认证用户才能访问
    return {"message": f"Hello {current_user.username}!"}
```

#### 获取当前用户信息

```python
async def some_function(current_user: Annotated[TokenData, Depends(require_auth)]):
    username = current_user.username
    # 使用用户名进行业务逻辑
```

### 安全注意事项

1. **生产环境**：务必修改 `JWT_SECRET_KEY` 为强密钥
2. **HTTPS**：生产环境必须使用 HTTPS
3. **令牌过期**：设置合理的令牌过期时间
4. **密码安全**：使用强密码并定期更换
5. **防暴力破解**：系统内置防暴力破解保护机制

### 防暴力破解保护

系统包含全面的防暴力破解保护机制：

- **失败尝试跟踪**：按IP地址跟踪失败的登录尝试
- **账户锁定**：超过最大失败尝试次数后临时锁定账户
- **频率限制**：限制每个IP地址每分钟的登录尝试次数
- **延迟响应**：失败尝试后增加延迟，提高攻击成本
- **自动清理**：定期清理旧记录，防止内存泄漏

#### 配置选项

- `MAX_FAILED_ATTEMPTS`：锁定前的最大失败尝试次数（默认：5）
- `LOCKOUT_DURATION`：锁定持续时间（秒）（默认：300 = 5分钟）
- `MAX_ATTEMPTS_PER_MINUTE`：每个IP每分钟最大尝试次数（默认：10）
- `FAILED_ATTEMPT_DELAY`：失败尝试后的延迟时间（秒）（默认：2）

#### 安全状态API

您可以检查当前IP地址的安全状态：

```bash
GET /api/v1/security/status
```

响应：
```json
{
  "ip_address": "127.0.0.1",
  "is_locked": false,
  "is_rate_limited": false,
  "failed_attempts": 0,
  "remaining_attempts": 5,
  "lockout_remaining": null,
  "recent_attempts_count": 0
}
```
