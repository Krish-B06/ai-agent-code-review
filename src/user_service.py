class UserService:
    def __init__(self):
        self.users = {}

    def create_user(self, user_id, name, email):
        # ❌ LOGICAL DEFECT 1: Missing State Validation (Allows duplicates/overwrites)
        # It silently overwrites an existing user with the same ID, destroying data integrity.
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
        # ❌ LOGICAL DEFECT 2: Blind State Mutation (KeyError / Crash Risk)
        # It attempts to delete a user key from the dictionary without verifying if it exists first.
        # This will throw a KeyError and crash the application if user_id is not found.
        del self.users[user_id]
        return True
