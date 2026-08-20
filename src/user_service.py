class UserService:
    def __init__(self):
        self.users = {}

    def create_user(self, user_id, name, email):
        user = {
            "id": user_id,
            "name": name,
            "email": email,
        }

        self.users[user_id] = user
        return user

    def get_user(self, user_id):
        return self.users.get(user_id)

    def delete_user(self, user_id):
        if user_id in self.users:
            del self.users[user_id]
            return True

        return False