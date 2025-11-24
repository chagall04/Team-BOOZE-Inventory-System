# src/app.py
"""Main application module for Team-BOOZE Inventory System.

This module handles the user interface and menu navigation.
"""

from .auth import login, create_account, delete_account
from .product_management import add_new_product
from .sales import record_sale, view_transaction_details, view_last_transaction  # scrum-74: added view_last_transaction
from .inventory_tracking import receive_new_stock, view_current_stock
from .reporting import generate_low_stock_report

# menu constants
ENTER_CHOICE_PROMPT = "Enter choice: "
INVALID_CHOICE_MSG = "Invalid choice, please try again."


def show_account_menu():
    """
    display account management menu
    scrum-17: create, delete accounts
    """
    print("\n--- Account Management ---")
    print("[1] Login")
    print("[2] Create Account")
    print("[3] Delete Account")
    print("[0] Exit")
    choice = input(ENTER_CHOICE_PROMPT)
    return choice


def handle_create_account():
    """handle account creation flow"""
    print("\n=== Create New Account ===")
    username = input("Username (min 3 characters): ")
    password = input("Password (min 6 characters): ")
    print("Role options: Manager, Clerk")
    role = input("Role: ")

    success, message = create_account(username, password, role)

    if success:
        print(f"\n{message}")
        return True

    print(f"\nError: {message}")
    return False


def handle_delete_account():
    """handle account deletion flow"""
    print("\n=== Delete Account ===")
    username = input("Username: ")
    password = input("Password: ")

    success, message = delete_account(username, password)

    if success:
        print(f"\n{message}")
        return True

    print(f"\nError: {message}")
    return False


def show_manager_menu():
    """display menu for manager role"""
    print("\n--- MANAGER MENU ---")
    while True:
        print("\n[1] Add/Update Product (Product Management)")
        print("[2] View Inventory Report (Reporting & Analytics)")
        print("[3] View Sales History (Sales Management)")
        print("[4] View Transaction Details (Sales Management)")
        print("[0] Log Out")
        choice = input(ENTER_CHOICE_PROMPT)

        if choice == '1':
            add_new_product()
        elif choice == '2':
            # scrum-58: hook up low stock report (SCRUM-14)
            threshold = input("Enter stock threshold (default 20): ").strip()
            try:
                threshold = int(threshold) if threshold else 20
                report = generate_low_stock_report(threshold)
                print(report)
            except ValueError:
                print("Invalid threshold. Using default of 20.")
                report = generate_low_stock_report(20)
                print(report)
        elif choice == '3':
            # scrum-15: view sales history (future sprint)
            print("Sales history function not yet implemented.")
        elif choice == '4':
            # scrum-64: view transaction details (SCRUM-60)
            view_transaction_details()
        elif choice == '0':
            print("Logging out...")
            break
        else:
            print(INVALID_CHOICE_MSG)


def show_clerk_menu():
    """display menu for clerk role"""
    print("\n--- CLERK MENU ---")
    while True:
        print("\n[1] Record a Sale (Sales Management)")
        print("[2] Receive New Stock (Inventory Tracking)")
        print("[3] View Product Stock (Inventory Tracking)")
        print("[4] View Transaction Details (Sales Management)")
        print("[5] View Last Sale (Sales Management)")  # scrum-74: added menu option
        print("[0] Log Out")
        choice = input(ENTER_CHOICE_PROMPT)

        if choice == '1':
            record_sale()
        elif choice == '2':
            receive_new_stock()
        elif choice == '3':
            view_current_stock()
        elif choice == '4':
            # scrum-51 & scrum-48: log product loss (SCRUM-10)
            log_product_loss()
        elif choice == '5':
            # scrum-64: view transaction details (SCRUM-60)
            view_transaction_details()
        elif choice == '5':
            # scrum-74: call new last sale function
            view_last_transaction()
        elif choice == '0':
            print("Logging out...")
            break
        else:
            print(INVALID_CHOICE_MSG)


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
            username = input("\nUsername: ")
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

        elif choice == '2':
            # create account flow
            handle_create_account()

        elif choice == '3':
            # delete account flow
            handle_delete_account()

        elif choice == '0':
            print("Goodbye!")
            break

        else:
            print(INVALID_CHOICE_MSG)


if __name__ == "__main__":
    main()
