import unittest
from unittest.mock import MagicMock
from src.user_service import UserService
from src.notification_service import NotificationService

class TestNotificationService(unittest.TestCase):
    def test_send_welcome_email_success(self):
        """Test that the welcome email is sent successfully for an existing user."""
        # Arrange
        mock_user_service = MagicMock(spec=UserService)
        mock_user_service.get_user.return_value = {"id": 1, "name": "Test User", "email": "test@example.com"}
        
        notification_service = NotificationService(user_service=mock_user_service)
        
        # Act
        result = notification_service.send_welcome_email(1)
        
        # Assert
        self.assertTrue(result)
        mock_user_service.get_user.assert_called_once_with(1)
