# src/auth.py
# user story scrum-17
# owned by: charlie gallagher

# authentication business logic
# sits between app.py (presentation) and database_manager.py (data)

import bcrypt
# import function from scrum-18
from src.database_manager import get_user_by_username 

def login(username, password):
    """
    handles scrum-21: hash input and get user role
    called by app.py for scrum-22
    """
    
    # get user hash and role from database
    user_data = get_user_by_username(username)
    
    if user_data:
        password_hash = user_data["hash"].encode('utf-8')
        user_password = password.encode('utf-8')
        
        # core of scrum-21: secure password comparison
        if bcrypt.checkpw(user_password, password_hash):
            # success: return user role
            return user_data["role"] 
            
    # failed login
    return None