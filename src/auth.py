# src/auth.py
# This file is for User Story SCRUM-17
# Owned by: Charlie Gallagher

# This module will contain the business logic for authentication.
# It will sit between the app.py (Presentation) and database_manager.py (Data) layers.

# TODO (Charlie): Implement SCRUM-21:
# This file will contain the main 'login(username, password)' function.
# It will:
# 1. Call a new 'get_user_by_username' function from database_manager.py.
# 2. Get the hashed password from the database.
# 3. Use 'bcrypt.checkpw' to compare the input password to the hash.
# 4. Return the user's 'role' (Manager/Clerk) on success or 'None' on failure.