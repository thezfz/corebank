"""认证服务单元测试"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta

from corebank.services.auth_service import AuthService
from corebank.models.user import User
from corebank.schemas.auth import UserCreate, UserLogin
from corebank.core.exceptions import AuthenticationError, ValidationError


class TestAuthService:
    """认证服务测试类"""

    @pytest.fixture
    def mock_user_repo(self):
        """模拟用户仓库"""
        return Mock()

    @pytest.fixture
    def auth_service(self, mock_user_repo):
        """认证服务实例"""
        return AuthService(user_repository=mock_user_repo)

    @pytest.fixture
    def sample_user(self):
        """示例用户数据"""
        return User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="$2b$12$hashed_password",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, mock_user_repo):
        """测试用户注册成功"""
        # 准备
        user_data = UserCreate(
            username="newuser",
            email="new@example.com",
            password="SecurePass123"
        )
        mock_user_repo.get_by_username.return_value = None
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.create.return_value = User(
            id=1,
            username="newuser",
            email="new@example.com",
            hashed_password="hashed",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # 执行
        result = await auth_service.register_user(user_data)

        # 验证
        assert result.username == "newuser"
        assert result.email == "new@example.com"
        mock_user_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_duplicate_username(self, auth_service, mock_user_repo, sample_user):
        """测试用户名重复注册"""
        # 准备
        user_data = UserCreate(
            username="testuser",
            email="new@example.com",
            password="SecurePass123"
        )
        mock_user_repo.get_by_username.return_value = sample_user

        # 执行和验证
        with pytest.raises(ValidationError, match="用户名已存在"):
            await auth_service.register_user(user_data)

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, mock_user_repo, sample_user):
        """测试用户认证成功"""
        # 准备
        login_data = UserLogin(username="testuser", password="correct_password")
        mock_user_repo.get_by_username.return_value = sample_user
        
        # Mock 密码验证
        auth_service._verify_password = Mock(return_value=True)

        # 执行
        result = await auth_service.authenticate_user(login_data)

        # 验证
        assert result == sample_user
        auth_service._verify_password.assert_called_once_with("correct_password", sample_user.hashed_password)

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_credentials(self, auth_service, mock_user_repo, sample_user):
        """测试无效凭据认证"""
        # 准备
        login_data = UserLogin(username="testuser", password="wrong_password")
        mock_user_repo.get_by_username.return_value = sample_user
        
        # Mock 密码验证失败
        auth_service._verify_password = Mock(return_value=False)

        # 执行和验证
        with pytest.raises(AuthenticationError, match="用户名或密码错误"):
            await auth_service.authenticate_user(login_data)

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, auth_service, mock_user_repo):
        """测试用户不存在认证"""
        # 准备
        login_data = UserLogin(username="nonexistent", password="password")
        mock_user_repo.get_by_username.return_value = None

        # 执行和验证
        with pytest.raises(AuthenticationError, match="用户名或密码错误"):
            await auth_service.authenticate_user(login_data)

    def test_create_access_token(self, auth_service):
        """测试创建访问令牌"""
        # 执行
        token = auth_service.create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(minutes=30)
        )

        # 验证
        assert isinstance(token, str)
        assert len(token) > 0

    def test_hash_password(self, auth_service):
        """测试密码哈希"""
        # 执行
        hashed = auth_service._hash_password("password123")

        # 验证
        assert hashed != "password123"
        assert hashed.startswith("$2b$")

    def test_verify_password(self, auth_service):
        """测试密码验证"""
        # 准备
        password = "password123"
        hashed = auth_service._hash_password(password)

        # 执行和验证
        assert auth_service._verify_password(password, hashed) is True
        assert auth_service._verify_password("wrong_password", hashed) is False
