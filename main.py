from app import db # Import the db module

def main():
    #The application's main entry point (CLI)
    print("---Team-BOOZE Inventory Management System---")
    # SCRUM-18 START: Connect to the database
    conn = db.connect()

    if conn is None:
        print("Exiting application due to database connection failure.")
        return
    
    try:
        # --- Placeholder for future sprint logic ---
        # Subtasks SCRUM-19, SCRUM-20, SCRUM-5 etc. will be implemented here.
        print("\n[SUCCESS] Foundational database connection established. Ready for schema creation (SCRUM-19).")

    finally:
        # SCRUM-18 END: Close the database connection
        db.close_connection(conn)

if __name__ == "__main__":
    main()


