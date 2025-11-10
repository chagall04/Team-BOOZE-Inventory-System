# src/reporting.py
# This file is for Epic SCRUM-4 (Reporting and Analytics)
# Owned by: Charlie Gallagher

"""This module contains logic for querying the DB and generating reports.

User Stories SCRUM-14, SCRUM-15, and SCRUM-16 are in the
"Upcoming" backlog and will be implemented in a future sprint.
"""

from .database_manager import get_low_stock_report


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
    report += "=" * 70 + "\n"
    report += f"LOW STOCK REPORT (Threshold: {threshold} units)\n"
    report += "=" * 70 + "\n"
    
    # if no low stock products, report accordingly
    if not low_stock_products:
        report += "\nGood news! All products are above the reorder threshold.\n"
        report += "=" * 70 + "\n"
        return report
    
    # format column headers
    report += f"\n{'ID':<5} {'Product Name':<25} {'Brand':<15} {'Stock':<8} {'Price':<10}\n"
    report += "-" * 70 + "\n"
    
    # format each product row
    for product in low_stock_products:
        product_id = product["id"]
        name = product["name"][:24]  # truncate if too long
        brand = product["brand"][:14] if product["brand"] else "N/A"
        quantity = product["quantity_on_hand"]
        price = product["price"]
        
        report += f"{product_id:<5} {name:<25} {brand:<15} {quantity:<8} €{price:<9.2f}\n"
    
    report += "-" * 70 + "\n"
    report += f"\nTotal products below threshold: {len(low_stock_products)}\n"
    report += "Recommendation: Reorder products listed above.\n"
    report += "=" * 70 + "\n"
    
    return report
