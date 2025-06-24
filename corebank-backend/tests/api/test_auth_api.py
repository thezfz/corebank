"""认证 API 集成测试"""
import pytest
from httpx import AsyncClient
from fastapi import status

from corebank.main import app


class TestAuthAPI:
    """认证 API 测试类"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_user_success(self):
        """测试用户注册成功"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 准备测试数据
            user_data = {
                "username": "testuser123",
                "email": "test123@example.com",
                "password": "SecurePass123"
            }

            # 执行请求
            response = await client.post("/api/v1/auth/register", json=user_data)

            # 验证响应
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["username"] == "testuser123"
            assert data["email"] == "test123@example.com"
            assert "id" in data
            assert "password" not in data  # 确保密码不在响应中

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_user_duplicate_username(self):
        """测试重复用户名注册"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 先注册一个用户
            user_data = {
                "username": "duplicate_user",
                "email": "first@example.com",
                "password": "SecurePass123"
            }
            await client.post("/api/v1/auth/register", json=user_data)

            # 尝试用相同用户名注册
            duplicate_data = {
                "username": "duplicate_user",
                "email": "second@example.com",
                "password": "AnotherPass123"
            }
            response = await client.post("/api/v1/auth/register", json=duplicate_data)

            # 验证响应
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "用户名已存在" in data["detail"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_user_invalid_password(self):
        """测试无效密码注册"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 弱密码
            user_data = {
                "username": "weakpass_user",
                "email": "weak@example.com",
                "password": "123"  # 太短且太简单
            }

            response = await client.post("/api/v1/auth/register", json=user_data)

            # 验证响应
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_login_success(self):
        """测试登录成功"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 先注册用户
            register_data = {
                "username": "logintest",
                "email": "login@example.com",
                "password": "LoginPass123"
            }
            await client.post("/api/v1/auth/register", json=register_data)

            # 登录
            login_data = {
                "username": "logintest",
                "password": "LoginPass123"
            }
            response = await client.post("/api/v1/auth/login", json=login_data)

            # 验证响应
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert "user" in data
            assert data["user"]["username"] == "logintest"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_login_invalid_credentials(self):
        """测试无效凭据登录"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 尝试用不存在的用户登录
            login_data = {
                "username": "nonexistent",
                "password": "WrongPass123"
            }
            response = await client.post("/api/v1/auth/login", json=login_data)

            # 验证响应
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert "用户名或密码错误" in data["detail"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_protected_endpoint_without_token(self):
        """测试未携带令牌访问受保护端点"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/users/me")

            # 验证响应
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_protected_endpoint_with_valid_token(self):
        """测试携带有效令牌访问受保护端点"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 注册并登录获取令牌
            register_data = {
                "username": "tokentest",
                "email": "token@example.com",
                "password": "TokenPass123"
            }
            await client.post("/api/v1/auth/register", json=register_data)

            login_data = {
                "username": "tokentest",
                "password": "TokenPass123"
            }
            login_response = await client.post("/api/v1/auth/login", json=login_data)
            token = login_response.json()["access_token"]

            # 使用令牌访问受保护端点
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get("/api/v1/users/me", headers=headers)

            # 验证响应
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["username"] == "tokentest"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_protected_endpoint_with_invalid_token(self):
        """测试携带无效令牌访问受保护端点"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 使用无效令牌
            headers = {"Authorization": "Bearer invalid_token"}
            response = await client.get("/api/v1/users/me", headers=headers)

            # 验证响应
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
