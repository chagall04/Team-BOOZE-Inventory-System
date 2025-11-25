# src/app.py
"""Main application module for Team-BOOZE Inventory System.

This module handles the user interface and menu navigation.
"""

from datetime import datetime

from colorama import init, Fore, Style

from .auth import login, create_account, delete_account
from .product_management import add_new_product
from .sales import (
    record_sale,
    view_transaction_details,
    view_last_transaction,
    view_sales_history  # scrum-15: added view_sales_history
)
from .inventory_tracking import receive_new_stock, view_current_stock, log_product_loss
from .reporting import (
    generate_low_stock_report,
    view_total_inventory_value,
    export_report
)
from .database_manager import (
    get_low_stock_report,
    get_total_inventory_value,
    get_all_transactions,
    get_all_products
)

# initialize colorama for windows support
init()

# menu constants
ENTER_CHOICE_PROMPT = f"{Fore.YELLOW}Enter choice: {Style.RESET_ALL}"
INVALID_CHOICE_MSG = f"{Fore.RED}Invalid choice. Try again or enter [Q] to go back.{Style.RESET_ALL}"

# session state
CURRENT_USER = None
CURRENT_ROLE = None
LOGIN_TIME = None


# --- helper functions for ux improvements ---

def normalize_choice(choice):
    """normalize menu choice - case insensitive, strip whitespace"""
    return choice.strip().upper() if choice else ""


def confirm_action(prompt="Are you sure?"):
    """
    prompt for confirmation with flexible yes/no input
    accepts: y, yes, n, no (case insensitive)
    returns: True for yes, False for no
    """
    while True:
        response = input(f"{Fore.YELLOW}{prompt} (yes/no): {Style.RESET_ALL}").strip().lower()
        if response in ('y', 'yes'):
            return True
        if response in ('n', 'no'):
            return False
        print(f"{Fore.YELLOW}Please enter 'yes' or 'no'.{Style.RESET_ALL}")


def is_quit(choice):
    """check if user wants to quit/go back"""
    return normalize_choice(choice) in ('Q', 'QUIT', 'EXIT', 'BACK')


def show_session_header():
    """display current session info at top of menu"""
    if CURRENT_USER and CURRENT_ROLE:
        role_color = Fore.MAGENTA if CURRENT_ROLE == "Manager" else Fore.BLUE
        time_str = LOGIN_TIME.strftime("%H:%M") if LOGIN_TIME else ""
        print(f"{Fore.WHITE}Logged in as: {Fore.CYAN}{CURRENT_USER}{Style.RESET_ALL} "
              f"({role_color}{CURRENT_ROLE}{Style.RESET_ALL}) "
              f"{Fore.WHITE}| Session started: {time_str}{Style.RESET_ALL}")


def show_dashboard():
    """display quick summary stats on login"""
    print(f"\n{Fore.CYAN}" + "─" * 50)
    print("  📊 QUICK DASHBOARD")
    print("─" * 50 + f"{Style.RESET_ALL}")
    
    # get stats
    low_stock = get_low_stock_report(20)
    total_value = get_total_inventory_value()
    transactions = get_all_transactions()
    products = get_all_products()
    
    # today's sales
    today = datetime.now().strftime("%Y-%m-%d")
    today_sales = [t for t in transactions if t['timestamp'].startswith(today)]
    today_revenue = sum(t['total_amount'] for t in today_sales)
    
    print(f"  {Fore.WHITE}Total Products:{Style.RESET_ALL} {len(products)}")
    print(f"  {Fore.WHITE}Inventory Value:{Style.RESET_ALL} {Fore.GREEN}€{total_value:,.2f}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Today's Sales:{Style.RESET_ALL} {len(today_sales)} "
          f"({Fore.GREEN}€{today_revenue:,.2f}{Style.RESET_ALL})")
    
    if low_stock:
        print(f"  {Fore.YELLOW}⚠ Low Stock Items:{Style.RESET_ALL} "
              f"{Fore.RED}{len(low_stock)}{Style.RESET_ALL} products below threshold")
    else:
        print(f"  {Fore.GREEN}✓ Stock Levels:{Style.RESET_ALL} All products above threshold")
    
    print(f"{Fore.CYAN}{'─' * 50}{Style.RESET_ALL}")


def show_account_menu():
    """
    display account management menu
    scrum-17: create, delete accounts
    """
    print(f"\n{Fore.CYAN}--- Account Management ---{Style.RESET_ALL}")
    print(f"{Fore.WHITE}[1]{Style.RESET_ALL} Login")
    print(f"{Fore.WHITE}[2]{Style.RESET_ALL} Create Account")
    print(f"{Fore.WHITE}[3]{Style.RESET_ALL} Delete Account")
    print(f"{Fore.WHITE}[0]{Style.RESET_ALL} Exit  {Fore.WHITE}[Q]{Style.RESET_ALL} Quit")
    choice = input(ENTER_CHOICE_PROMPT)
    return normalize_choice(choice)


def handle_create_account():
    """handle account creation flow"""
    print(f"\n{Fore.CYAN}=== Create New Account ==={Style.RESET_ALL}")
    username = input(f"{Fore.YELLOW}Username (min 3 characters): {Style.RESET_ALL}")
    password = input(f"{Fore.YELLOW}Password (min 6 characters): {Style.RESET_ALL}")
    print(f"Role options: {Fore.MAGENTA}Manager{Style.RESET_ALL}, {Fore.BLUE}Clerk{Style.RESET_ALL}")
    role = input(f"{Fore.YELLOW}Role: {Style.RESET_ALL}")

    success, message = create_account(username, password, role)

    if success:
        print(f"\n{Fore.GREEN}{message}{Style.RESET_ALL}")
        return True

    print(f"\n{Fore.RED}Error: {message}{Style.RESET_ALL}")
    return False


def handle_delete_account():
    """handle account deletion flow with confirmation"""
    print(f"\n{Fore.CYAN}=== Delete Account ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Enter [Q] at any prompt to cancel.{Style.RESET_ALL}")
    
    username = input(f"{Fore.YELLOW}Username: {Style.RESET_ALL}").strip()
    if is_quit(username):
        print(f"{Fore.YELLOW}Cancelled.{Style.RESET_ALL}")
        return False
    
    password = input(f"{Fore.YELLOW}Password: {Style.RESET_ALL}")
    if is_quit(password):
        print(f"{Fore.YELLOW}Cancelled.{Style.RESET_ALL}")
        return False
    
    # confirmation before destructive action
    print(f"\n{Fore.RED}⚠ Warning: This action cannot be undone!{Style.RESET_ALL}")
    if not confirm_action(f"Delete account '{username}'?"):
        print(f"{Fore.YELLOW}Deletion cancelled.{Style.RESET_ALL}")
        return False

    success, message = delete_account(username, password)

    if success:
        print(f"\n{Fore.GREEN}{message}{Style.RESET_ALL}")
        return True

    print(f"\n{Fore.RED}Error: {message}{Style.RESET_ALL}")
    return False


def handle_view_low_stock_report():
    """
    scrum-58: handle low stock report display
    prompts for threshold and displays report
    """
    threshold = input(f"{Fore.YELLOW}Enter stock threshold (default 20): {Style.RESET_ALL}").strip()
    try:
        threshold = int(threshold) if threshold else 20
    except ValueError:
        print(f"{Fore.YELLOW}Invalid threshold. Using default of 20.{Style.RESET_ALL}")
        threshold = 20
    
    report = generate_low_stock_report(threshold)
    print(report)


def handle_export_report():
    """
    scrum-16: handle export report menu flow
    prompts user for report type, format, and filename
    
    returns:
        bool: True if export successful, False otherwise
    """
    print(f"\n{Fore.CYAN}=== Export Report ==={Style.RESET_ALL}")
    
    # select report type
    print(f"\n{Fore.WHITE}Select report to export:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}[1]{Style.RESET_ALL} Low Stock Report")
    print(f"{Fore.WHITE}[2]{Style.RESET_ALL} Inventory Report")
    report_choice = input(ENTER_CHOICE_PROMPT).strip()
    
    if report_choice == '1':
        report_type = 'low_stock'
    elif report_choice == '2':
        report_type = 'inventory'
    else:
        print(INVALID_CHOICE_MSG)
        return False
    
    # select file format
    print(f"\n{Fore.WHITE}Select export format:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}[1]{Style.RESET_ALL} CSV")
    print(f"{Fore.WHITE}[2]{Style.RESET_ALL} JSON")
    format_choice = input(ENTER_CHOICE_PROMPT).strip()
    
    if format_choice == '1':
        file_format = 'csv'
        extension = '.csv'
    elif format_choice == '2':
        file_format = 'json'
        extension = '.json'
    else:
        print(INVALID_CHOICE_MSG)
        return False
    
    # get filename from user
    filename = input(f"{Fore.YELLOW}Enter filename (without extension): {Style.RESET_ALL}").strip()
    
    if not filename:
        print(f"{Fore.RED}Error: Filename cannot be empty.{Style.RESET_ALL}")
        return False
    
    # add extension if not present
    full_filename = filename if filename.endswith(extension) else filename + extension
    
    # perform the export
    success, message = export_report(report_type, file_format, full_filename)
    
    if success:
        print(f"\n{Fore.GREEN}{message}{Style.RESET_ALL}")
        return True
    
    print(f"\n{Fore.RED}Error: {message}{Style.RESET_ALL}")
    return False


def show_manager_menu():
    """display menu for manager role"""
    print(f"\n{Fore.MAGENTA}" + "═" * 40)
    print("         MANAGER MENU")
    print("═" * 40 + f"{Style.RESET_ALL}")
    show_session_header()
    
    while True:
        print(f"\n{Fore.WHITE}[1]{Style.RESET_ALL} Add/Update Product {Fore.CYAN}(Product Management){Style.RESET_ALL}")
        print(f"{Fore.WHITE}[2]{Style.RESET_ALL} View Inventory Report {Fore.CYAN}(Reporting & Analytics){Style.RESET_ALL}")
        print(f"{Fore.WHITE}[3]{Style.RESET_ALL} View Sales History {Fore.CYAN}(Sales Management){Style.RESET_ALL}")
        print(f"{Fore.WHITE}[4]{Style.RESET_ALL} View Transaction Details {Fore.CYAN}(Sales Management){Style.RESET_ALL}")
        print(f"{Fore.WHITE}[5]{Style.RESET_ALL} View Total Inventory Value {Fore.CYAN}(Reporting & Analytics){Style.RESET_ALL}")
        print(f"{Fore.WHITE}[6]{Style.RESET_ALL} Export Report {Fore.CYAN}(Reporting & Analytics){Style.RESET_ALL}")
        print(f"{Fore.WHITE}[0]{Style.RESET_ALL} Log Out  {Fore.WHITE}[Q]{Style.RESET_ALL} Quit")
        choice = normalize_choice(input(ENTER_CHOICE_PROMPT))

        if choice == '1':
            add_new_product()
        elif choice == '2':
            # scrum-58: hook up low stock report (SCRUM-14)
            handle_view_low_stock_report()
        elif choice == '3':
            # scrum-15: view sales history
            view_sales_history()
        elif choice == '4':
            # scrum-64: view transaction details (SCRUM-60)
            view_transaction_details()
        elif choice == '5':
            # view total inventory value report
            view_total_inventory_value()
        elif choice == '6':
            # scrum-16: export report to file
            handle_export_report()
        elif choice in ('0', 'Q', 'QUIT'):
            print(f"{Fore.YELLOW}Logging out...{Style.RESET_ALL}")
            break
        else:
            print(INVALID_CHOICE_MSG)


def show_clerk_menu():
    """display menu for clerk role"""
    print(f"\n{Fore.BLUE}" + "═" * 40)
    print("          CLERK MENU")
    print("═" * 40 + f"{Style.RESET_ALL}")
    show_session_header()
    
    while True:
        print(f"\n{Fore.WHITE}[1]{Style.RESET_ALL} Record a Sale {Fore.CYAN}(Sales Management){Style.RESET_ALL}")
        print(f"{Fore.WHITE}[2]{Style.RESET_ALL} Receive New Stock {Fore.CYAN}(Inventory Tracking){Style.RESET_ALL}")
        print(f"{Fore.WHITE}[3]{Style.RESET_ALL} View Product Stock {Fore.CYAN}(Inventory Tracking){Style.RESET_ALL}")
        print(f"{Fore.WHITE}[4]{Style.RESET_ALL} Log Product Loss {Fore.CYAN}(Inventory Tracking){Style.RESET_ALL}")
        print(f"{Fore.WHITE}[5]{Style.RESET_ALL} View Transaction Details {Fore.CYAN}(Sales Management){Style.RESET_ALL}")
        print(f"{Fore.WHITE}[6]{Style.RESET_ALL} View Last Sale {Fore.CYAN}(Sales Management){Style.RESET_ALL}")
        print(f"{Fore.WHITE}[0]{Style.RESET_ALL} Log Out  {Fore.WHITE}[Q]{Style.RESET_ALL} Quit")
        choice = normalize_choice(input(ENTER_CHOICE_PROMPT))

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
        elif choice == '6':
            # scrum-74: call new last sale function
            view_last_transaction()
        elif choice in ('0', 'Q', 'QUIT'):
            print(f"{Fore.YELLOW}Logging out...{Style.RESET_ALL}")
            break
        else:
            print(INVALID_CHOICE_MSG)


def main():
    """
    main application entry point
    handles scrum-22: integrate login prompt and role-based access
    scrum-17: account management integration
    """
    global CURRENT_USER, CURRENT_ROLE, LOGIN_TIME  # pylint: disable=global-statement
    
    print(f"\n{Fore.GREEN}" + "═" * 50)
    print("   Welcome to the Team-BOOZE Inventory System")
    print("═" * 50 + f"{Style.RESET_ALL}")

    while True:
        choice = show_account_menu()

        if choice == '1':
            # login flow
            print(f"\n{Fore.YELLOW}Enter [Q] to cancel login.{Style.RESET_ALL}")
            username = input(f"{Fore.YELLOW}Username: {Style.RESET_ALL}").strip()
            if is_quit(username):
                continue
            
            password = input(f"{Fore.YELLOW}Password: {Style.RESET_ALL}")
            if is_quit(password):
                continue

            # delegate login logic to auth module (scrum-21)
            role = login(username, password)

            # route to correct menu based on role
            if role == "Manager":
                # set session state
                CURRENT_USER = username
                CURRENT_ROLE = role
                LOGIN_TIME = datetime.now()
                
                print(f"\n{Fore.GREEN}✓ Login successful. Welcome, {username}!{Style.RESET_ALL}")
                show_dashboard()
                show_manager_menu()
                
                # clear session on logout
                CURRENT_USER = None
                CURRENT_ROLE = None
                LOGIN_TIME = None
                
            elif role == "Clerk":
                # set session state
                CURRENT_USER = username
                CURRENT_ROLE = role
                LOGIN_TIME = datetime.now()
                
                print(f"\n{Fore.GREEN}✓ Login successful. Welcome, {username}!{Style.RESET_ALL}")
                show_dashboard()
                show_clerk_menu()
                
                # clear session on logout
                CURRENT_USER = None
                CURRENT_ROLE = None
                LOGIN_TIME = None
            else:
                # fulfills scrum-17 acceptance criteria
                print(f"\n{Fore.RED}✗ Access denied: Invalid username or password.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Hint: Check your credentials or create a new account.{Style.RESET_ALL}")

        elif choice == '2':
            # create account flow
            handle_create_account()

        elif choice == '3':
            # delete account flow
            handle_delete_account()

        elif choice in ('0', 'Q', 'QUIT'):
            print(f"\n{Fore.GREEN}Goodbye! Thank you for using Team-BOOZE.{Style.RESET_ALL}")
            break

        else:
            print(INVALID_CHOICE_MSG)


if __name__ == "__main__":
    main()
