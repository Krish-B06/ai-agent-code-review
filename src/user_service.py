import sqlite3

class UserService:
    def __init__(self):
        self.users = {}

    def create_user(self, user_id, name, email):
        # ❌ LOGICAL DEFECT 1: Missing State Validation (Allows duplicates/overwrites)
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
        del self.users[user_id]
        return True
    
    def get_user(self, user_id, include_profile=False): # Add a new parameter
        # This change breaks NotificationService, which calls get_user(user_id)
        print(f"Fetching user with profile status: {include_profile}")
        return self.users.get(user_id)

    def search_users_by_raw_query(self, query):
        # ❌ CRITICAL SECURITY DEFECT: SQL Injection Risk
        # ❌ CRITICAL PERFORMANCE DEFECT: Direct connection opened and never closed/returned
        import sqlite3
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        
        # Unsafe string formatting allows SQL injection attacks
        raw_sql = f"SELECT * FROM users WHERE name = '{query}'"
        cursor.execute(raw_sql)
        
        results = cursor.fetchall()
        # Missing conn.close() which causes connection and memory leaks under load
        return results

    def sync_with_billing_service(self, user_id):
        # ❌ NEW CRITICAL SECURITY DEFECT: Hardcoded Secret (Safe dummy version)
        # Our AI agent will still identify this as a security leak, but GitHub will allow the push!
        api_key = "DUMMY_SECRET_KEY_FOR_TESTING_12345" 
        
        print(f"Connecting to billing service for user {user_id} with key {api_key[:10]}...")
        return {"status": "synced", "user_id": user_id}
