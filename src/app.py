# src/app.py

from auth import login
from src.product_management import add_new_product

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
    """
    print("--- Welcome to the Team-BOOZE Inventory Tracking System ---")
    
    # get user input
    username = input("Username: ")
    password = input("Password: ")
    
    # delegate login logic to auth module (scrum-21)
    role = login(username, password)
    
    # route to correct menu based on role
    if role == "Manager":
        print(f"\nLogin successful. Welcome, {username} (Manager).")
        show_manager_menu()
    elif role == "Clerk":
        print(f"\nLogin successful. Welcome, {username} (Clerk).")
        show_clerk_menu()
    else:
        # fulfills scrum-17 acceptance criteria
        print("Access denied: Invalid username or password.")

if __name__ == "__main__":
    main()