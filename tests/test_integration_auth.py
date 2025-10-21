# tests/test_integration_auth.py
import pytest
import sqlite3
import bcrypt

# import the functions we are testing
from src.auth import login
from src.database_manager import get_user_by_username

@pytest.fixture
def setup_test_database(tmp_path):
    """
    pytest fixture. runs before each test function.
    creates fresh, temporary database for each test.
    """
    # use temporary file for database
    db_path = tmp_path / "test_inventory.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # create necessary 'users' table
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    );
    """)

    # add default users with known passwords
    manager_pass = bcrypt.hashpw(b"manager123", bcrypt.gensalt())
    clerk_pass = bcrypt.hashpw(b"clerk123", bcrypt.gensalt())
    
    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                   ("manager", manager_pass.decode('utf-8'), "Manager"))
    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                   ("clerk", clerk_pass.decode('utf-8'), "Clerk"))

    conn.commit()
    conn.close()

    # return path to test database
    return str(db_path)

def test_login_integration_success_manager(setup_test_database, monkeypatch):
    """
    tests full login flow for manager against real test database.
    """
    # override db_name in database_manager module to use test db
    monkeypatch.setattr('src.database_manager.DB_NAME', setup_test_database)

    # call login function with correct credentials
    role = login("manager", "manager123")

    # check result
    assert role == "Manager"

def test_login_integration_success_clerk(setup_test_database, monkeypatch):
    """
    tests full login flow for clerk against real test database.
    """
    monkeypatch.setattr('src.database_manager.DB_NAME', setup_test_database)

    role = login("clerk", "clerk123")

    assert role == "Clerk"

def test_login_integration_failure_wrong_password(setup_test_database, monkeypatch):
    """
    tests login flow with wrong password.
    """
    monkeypatch.setattr('src.database_manager.DB_NAME', setup_test_database)
    
    role = login("manager", "wrongpassword")
    
    assert role is None

def test_login_integration_failure_user_not_found(setup_test_database, monkeypatch):
    """
    tests login flow with user that does not exist.
    """
    monkeypatch.setattr('src.database_manager.DB_NAME', setup_test_database)
    
    role = login("nosuchuser", "password")
    
    assert role is None