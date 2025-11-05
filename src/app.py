# src/app.py

from .auth import login, create_account, delete_account
from .product_management import add_new_product


def show_account_menu():
    """
    display account management menu
    scrum-17: create, delete accounts
    """
    print("\n--- account management ---")
    print("[1] login")
    print("[2] create account")
    print("[3] delete account")
    print("[0] exit")
    choice = input("enter choice: ")
    return choice


def handle_create_account():
    """handle account creation flow"""
    print("\n=== create new account ===")
    username = input("username (min 3 characters): ")
    password = input("password (min 6 characters): ")
    print("role options: Manager, Clerk")
    role = input("role: ")
    
    success, message = create_account(username, password, role)
    
    if success:
        print(f"\n{message}")
        return True
    else:
        print(f"\nerror: {message}")
        return False


def handle_delete_account():
    """handle account deletion flow"""
    print("\n=== delete account ===")
    username = input("username: ")
    password = input("password: ")
    
    success, message = delete_account(username, password)
    
    if success:
        print(f"\n{message}")
        return True
    else:
        print(f"\nerror: {message}")
        return False

def show_manager_menu():
    """display menu for manager role"""
    print("\n--- MANAGER MENU ---")
    while True:
        print("\n[1] Add/Update Product (Product Management)")
        print("[2] View Inventory Report (Reporting & Analytics)")
        print("[3] View Sales History (Sales Management)")
        print("[0] Log Out")
        choice = input("Enter choice: ")
        
        if choice == '1':
            add_new_product()
        elif choice == '2':
            # todo: hook up charlie's reporting functions here
            print("Reporting function not yet implemented.")
        elif choice == '3':
            # todo: hook up sara's view_sales_history() here
            print("Sales history function not yet implemented.")
        elif choice == '0':
            print("Logging out...")
            break
        else:
            print("Invalid choice, please try again.")

def show_clerk_menu():
    """display menu for clerk role"""
    print("\n--- CLERK MENU ---")
    while True:
        print("\n[1] Record a Sale (Sales Management)")
        print("[2] Receive New Stock (Inventory Tracking)")
        print("[3A] View Product Stock (Inventory Tracking)")
        print("[0] Log Out")
        choice = input("Enter choice: ")

        if choice == '1':
            # todo: hook up sara's record_sale() here
            print("Sales function not yet implemented.")
        elif choice == '2':
            # todo: hook up séan's receive_new_stock() here
            print("Receive stock function not yet implemented.")
        elif choice == '3':
            # todo: hook up séan's view_current_stock() here
            print("View stock function not yet implemented.")
        elif choice == '0':
            print("Logging out...")
            break
        else:
            print("Invalid choice, please try again.")

def main():
    """
    main application entry point
    handles scrum-22: integrate login prompt and role-based access
    scrum-17: account management integration
    """
    print("--- Welcome to the Team-BOOZE Inventory Tracking System ---")
    
    while True:
        choice = show_account_menu()
        
        if choice == '1':
            # login flow
            username = input("\nusername: ")
            password = input("password: ")
            
            # delegate login logic to auth module (scrum-21)
            role = login(username, password)
            
            # route to correct menu based on role
            if role == "Manager":
                print(f"\nlogin successful. welcome, {username} (manager).")
                show_manager_menu()
            elif role == "Clerk":
                print(f"\nlogin successful. welcome, {username} (clerk).")
                show_clerk_menu()
            else:
                # fulfills scrum-17 acceptance criteria
                print("access denied: invalid username or password.")
        
        elif choice == '2':
            # create account flow
            handle_create_account()
        
        elif choice == '3':
            # delete account flow
            handle_delete_account()
        
        elif choice == '0':
            print("goodbye!")
            break
        
        else:
            print("invalid choice, please try again.")

if __name__ == "__main__":
    main()