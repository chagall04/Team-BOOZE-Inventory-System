# src/auth.py
# user story scrum-17
# owned by: charlie gallagher

# authentication business logic
# sits between app.py (presentation) and database_manager.py (data)

import bcrypt
# import function from scrum-18
from .database_manager import get_user_by_username, create_user, delete_user


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


def create_account(username, password, role):
    """
    scrum-17: create new account with validation
    returns (success, message)
    """
    # validate inputs
    if not username or len(username.strip()) < 3:
        return False, "username must be at least 3 characters"
    
    if not password or len(password) < 6:
        return False, "password must be at least 6 characters"
    
    if role not in ["Manager", "Clerk"]:
        return False, "role must be Manager or Clerk"
    
    # create user in database
    success, result = create_user(username, password, role)
    
    if success:
        return True, f"account created successfully"
    
    return False, result


def delete_account(username, password):
    """
    scrum-17: delete account with password verification
    returns (success, message)
    """
    # validate username
    if not username or len(username.strip()) == 0:
        return False, "username is required"
    
    # prevent deleting default accounts
    if username in ["manager", "clerk"]:
        return False, "cannot delete default accounts"
    
    # verify password before deletion
    user_data = get_user_by_username(username)
    if not user_data:
        return False, "user not found"
    
    password_hash = user_data["hash"].encode('utf-8')
    user_password = password.encode('utf-8')
    
    if not bcrypt.checkpw(user_password, password_hash):
        return False, "incorrect password"
    
    # delete user from database
    success, message = delete_user(username)
    
    return success, message