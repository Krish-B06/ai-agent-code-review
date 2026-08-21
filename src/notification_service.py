from .user_service import UserService

class NotificationService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def send_welcome_email(self, user_id):
        """Fetches a user and sends them a welcome email."""
        user = self.user_service.get_user(user_id)
        
        if user:
            print(f"Email sent to {user['name']} at {user['email']}.")
            return True
        else:
            print(f"Failed to send email: User with ID {user_id} not found.")
            return False
