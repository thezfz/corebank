"""用户仓库单元测试"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import Mock, AsyncMock

from corebank.repositories.postgres_repo import PostgresRepository
from corebank.models.user import User
from corebank.schemas.user import UserCreate


class TestUserRepository:
    """用户仓库测试类"""

    @pytest.fixture
    def mock_session(self):
        """模拟数据库会话"""
        session = Mock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = Mock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def user_repo(self, mock_session):
        """用户仓库实例"""
        return UserRepository(session=mock_session)

    @pytest.fixture
    def sample_user_data(self):
        """示例用户数据"""
        return UserCreate(
            username="testuser",
            email="test@example.com",
            password="hashed_password"
        )

    @pytest.mark.asyncio
    async def test_create_user(self, user_repo, mock_session, sample_user_data):
        """测试创建用户"""
        # 执行
        result = await user_repo.create(sample_user_data)

        # 验证
        assert isinstance(result, User)
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_username_found(self, user_repo, mock_session):
        """测试根据用户名查找用户 - 找到"""
        # 准备
        mock_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed"
        )
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        # 执行
        result = await user_repo.get_by_username("testuser")

        # 验证
        assert result == mock_user
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_username_not_found(self, user_repo, mock_session):
        """测试根据用户名查找用户 - 未找到"""
        # 准备
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # 执行
        result = await user_repo.get_by_username("nonexistent")

        # 验证
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_email_found(self, user_repo, mock_session):
        """测试根据邮箱查找用户 - 找到"""
        # 准备
        mock_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed"
        )
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        # 执行
        result = await user_repo.get_by_email("test@example.com")

        # 验证
        assert result == mock_user
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, user_repo, mock_session):
        """测试根据ID查找用户 - 找到"""
        # 准备
        mock_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed"
        )
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        # 执行
        result = await user_repo.get_by_id(1)

        # 验证
        assert result == mock_user
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user(self, user_repo, mock_session):
        """测试更新用户"""
        # 准备
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed"
        )
        update_data = {"email": "newemail@example.com"}

        # 执行
        result = await user_repo.update(user, update_data)

        # 验证
        assert result.email == "newemail@example.com"
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user(self, user_repo, mock_session):
        """测试删除用户"""
        # 准备
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed"
        )

        # 执行
        await user_repo.delete(user)

        # 验证
        mock_session.delete.assert_called_once_with(user)
        mock_session.commit.assert_called_once()
