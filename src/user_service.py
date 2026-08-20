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

    def GetUser(self, USER_ID):
        return self.users.get(USER_ID)

    def delete_user(self, user_id):
        if user_id in self.users:
            del self.users[user_id]
            return True

        return False