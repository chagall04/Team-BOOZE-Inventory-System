# src/reporting.py
# This file is for Epic SCRUM-4 (Reporting and Analytics)
# Owned by: Charlie Gallagher

"""This module contains logic for querying the DB and generating reports.

Implements SCRUM-14 (low stock report), SCRUM-15 (inventory value), and
SCRUM-16 (export reports to CSV/JSON).
"""

import csv
import json
import os

from colorama import Fore, Style

from .database_manager import get_low_stock_report, get_total_inventory_value, get_all_products

# scrum-16: protected filenames that cannot be overwritten
PROTECTED_FILES = [
    "inventory.db",
    "main.py",
    "app.py",
    "auth.py",
    "database_manager.py",
    "inventory_tracking.py",
    "product_management.py",
    "reporting.py",
    "sales.py",
    "__init__.py",
]


def format_currency(value):
    """
    format a numeric value as currency with Euro symbol and two decimal places
    
    args:
        value: numeric value to format (int or float)
    
    returns:
        formatted string with Euro symbol and two decimals (e.g., "€1,250.00")
    """
    # format with thousands separator and two decimal places
    return f"€{value:,.2f}"


def generate_low_stock_report(threshold=20):
    """
    scrum-57: generate low stock report by querying database
    displays all products with quantity below threshold
    
    args:
        threshold: stock level threshold in units (default: 20)
    
    returns:
        formatted report string for display to user
        includes product details and reorder recommendations
    """
    # query database for low stock products
    low_stock_products = get_low_stock_report(threshold)
    
    # format report header
    report = "\n"
    report += f"{Fore.CYAN}" + "=" * 70 + "\n"
    report += f"LOW STOCK REPORT (Threshold: {threshold} units)\n"
    report += "=" * 70 + f"{Style.RESET_ALL}\n"
    
    # if no low stock products, report accordingly
    if not low_stock_products:
        report += f"\n{Fore.GREEN}Good news! All products are above the reorder threshold.{Style.RESET_ALL}\n"
        report += f"{Fore.CYAN}" + "=" * 70 + f"{Style.RESET_ALL}\n"
        return report
    
    # format column headers
    report += f"\n{Fore.WHITE}{'ID':<5} {'Product Name':<25} {'Brand':<15} {'Stock':<8} {'Price':<10}{Style.RESET_ALL}\n"
    report += "-" * 70 + "\n"
    
    # format each product row
    for product in low_stock_products:
        product_id = product["id"]
        name = product["name"][:25]  # truncate if too long
        brand = product["brand"][:15] if product["brand"] else "N/A"
        quantity = product["quantity_on_hand"]
        price = product["price"]
        
        # color stock red if very low (below 5), yellow if low
        if quantity < 5:
            stock_color = Fore.RED
        else:
            stock_color = Fore.YELLOW
        
        report += f"{product_id:<5} {name:<25} {brand:<15} {stock_color}{quantity:<8}{Style.RESET_ALL} {Fore.GREEN}€{price:<9.2f}{Style.RESET_ALL}\n"
    
    report += "-" * 70 + "\n"
    report += f"\n{Fore.YELLOW}Total products below threshold: {len(low_stock_products)}{Style.RESET_ALL}\n"
    report += f"{Fore.YELLOW}Recommendation: Reorder products listed above.{Style.RESET_ALL}\n"
    report += f"{Fore.CYAN}" + "=" * 70 + f"{Style.RESET_ALL}\n"
    
    return report


def view_total_inventory_value():
    """
    generate and display total inventory value report
    queries database for total value of all products in stock
    
    displays formatted report to user showing total inventory value
    """
    # query database for total value
    total_value = get_total_inventory_value()
    
    # format report
    report = "\n"
    report += f"{Fore.CYAN}" + "=" * 70 + "\n"
    report += "TOTAL INVENTORY VALUE REPORT\n"
    report += "=" * 70 + f"{Style.RESET_ALL}\n"
    report += f"\nTotal value of all products in stock: {Fore.GREEN}{format_currency(total_value)}{Style.RESET_ALL}\n"
    report += f"{Fore.CYAN}" + "=" * 70 + f"{Style.RESET_ALL}\n"
    
    print(report)


# scrum-16: export report functions

def export_to_csv(data, filename):
    """
    export list of dictionaries to csv file
    
    args:
        data: list of dicts with consistent keys
        filename: output file path
    
    returns:
        tuple (success: bool, message: str)
    """
    # handle empty data
    if not data:
        return False, "No data to export"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # use keys from first dict as fieldnames
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(data)
        
        return True, f"Successfully exported to {filename}"
    except (OSError, IOError) as e:
        return False, f"Failed to write file: {str(e)}"


def export_to_json(data, filename):
    """
    export data to json file with proper indentation
    
    args:
        data: data to serialize (typically list of dicts)
        filename: output file path
    
    returns:
        tuple (success: bool, message: str)
    """
    try:
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=4)
        
        return True, f"Successfully exported to {filename}"
    except (OSError, IOError) as e:
        return False, f"Failed to write file: {str(e)}"
    except (TypeError, ValueError) as e:
        return False, f"Failed to serialize data: {str(e)}"


def is_protected_filename(filename):
    """
    check if filename matches a protected system file
    
    args:
        filename: filename to check (can include path)
    
    returns:
        bool: True if file is protected and should not be overwritten
    """
    # extract just the filename from path
    base_name = os.path.basename(filename)
    
    # check against protected list (case insensitive)
    return base_name.lower() in [f.lower() for f in PROTECTED_FILES]


def export_report(report_type, file_format, filename):
    """
    main export function - orchestrates data prep and file export
    
    args:
        report_type: 'low_stock' or 'inventory'
        file_format: 'csv' or 'json'
        filename: output filename
    
    returns:
        tuple (success: bool, message: str)
    """
    # validate filename is not protected
    if is_protected_filename(filename):
        return False, f"Cannot overwrite protected file: {filename}"
    
    # prepare data based on report type
    if report_type == 'low_stock':
        data = get_low_stock_report(20)  # default threshold
    elif report_type == 'inventory':
        data = get_all_products()
    else:
        return False, f"Unknown report type: {report_type}"
    
    # export based on format
    if file_format == 'csv':
        return export_to_csv(data, filename)
    if file_format == 'json':
        return export_to_json(data, filename)
    
    return False, f"Unknown file format: {file_format}"
