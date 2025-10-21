# init_db.py
import sqlite3

DB_NAME = "inventory.db"

# Sample data for the 'booze' table
booze_data = [
    ('Jameson Original', 'Jameson', 'Whiskey', 40.0, 700, 'Ireland', 30.50, 50, 'The classic, super smooth, triple-distilled Irish whiskey.'),
    ('Guinness Draught', 'Guinness', 'Stout', 4.2, 500, 'Ireland', 2.80, 200, 'The iconic Irish dry stout. Sold per 500ml can.'),
    ('Bulmers Original Irish Cider', 'Bulmers', 'Cider', 4.5, 500, 'Ireland', 2.90, 150, 'The original crisp Irish cider. Sold per 500ml bottle.'),
    ('Smirnoff Vodka', 'Smirnoff', 'Vodka', 37.5, 700, 'Russia', 24.50, 80, 'The world''s number one vodka. Triple distilled.'),
    ('Powers Gold Label', 'Powers', 'Whiskey', 40.0, 700, 'Ireland', 32.00, 45, 'A classic Irish whiskey, full-bodied with a spicy, honeyed flavour.'),
    ('Dingle Gin', 'Dingle', 'Gin', 42.5, 700, 'Ireland', 38.00, 30, 'An award-winning artisanal gin from Kerry, with local botanicals.'),
    ('Captain Morgan Spiced Gold', 'Captain Morgan', 'Rum', 35.0, 700, 'Jamaica', 26.00, 60, 'The classic spiced rum. Rich vanilla and caramel notes.'),
    ('Heineken', 'Heineken', 'Lager', 4.3, 500, 'Netherlands', 3.00, 180, 'A premium, globally recognised lager. Sold per 500ml bottle.'),
    ('Baileys Irish Cream', 'Baileys', 'Liqueur', 17.0, 700, 'Ireland', 25.00, 40, 'The original Irish cream. Irish whiskey, cream, and chocolate.'),
    ('Bacardi Superior', 'Bacardi', 'Rum', 37.5, 700, 'Cuba', 25.50, 55, 'The classic white rum for all your cocktails. Clean and crisp.'),
    ('Cork Dry Gin', 'Cork Dry', 'Gin', 37.5, 700, 'Ireland', 24.00, 70, 'A true Irish classic. A crisp, traditional London Dry style gin.'),
    ('Hophouse 13', 'Guinness', 'Lager', 4.1, 500, 'Ireland', 2.90, 130, 'A modern lager from Guinness. Crisp and hoppy.'),
    ('Bushmills Original', 'Bushmills', 'Whiskey', 40.0, 700, 'Ireland', 29.00, 40, 'A smooth, triple-distilled blend from Ireland''s oldest distillery.'),
    ('Bombay Sapphire', 'Bombay', 'Gin', 40.0, 700, 'England', 34.00, 35, 'A benchmark London Dry Gin with vapour-infused botanicals.'),
    ('Jack Daniel''s Old No. 7', 'Jack Daniel''s', 'Whiskey', 40.0, 700, 'USA', 33.00, 50, 'The world''s best-selling Tennessee whiskey. Charcoal mellowed.')
]

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Drop tables to ensure a fresh start
print("Dropping old tables...")
cursor.execute("DROP TABLE IF EXISTS transaction_items;")
cursor.execute("DROP TABLE IF EXISTS transactions;")
cursor.execute("DROP TABLE IF EXISTS booze;")
cursor.execute("DROP TABLE IF EXISTS users;") # In case it exists from old versions

# Create booze table
print("Creating 'booze' table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS booze (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    brand TEXT,
    type TEXT,
    abv REAL,
    volume_ml INTEGER,
    origin_country TEXT,
    price REAL NOT NULL,
    quantity_on_hand INTEGER DEFAULT 0,
    description TEXT
);
""")

# Create transactions table
print("Creating 'transactions' table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    total_amount REAL NOT NULL
);
""")

# Create transaction_items table
print("Creating 'transaction_items' table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS transaction_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price_at_sale REAL NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions (transaction_id),
    FOREIGN KEY (product_id) REFERENCES booze (id)
);
""")

# Populate the 'booze' table
try:
    print(f"Adding {len(booze_data)} sample products...")
    cursor.executemany("""
    INSERT INTO booze (name, brand, type, abv, volume_ml, origin_country, price, quantity_on_hand, description) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, booze_data)
    print("Sample products added.")
except sqlite3.IntegrityError:
    print("Sample products already exist.")


conn.commit()
conn.close()

print(f"Database '{DB_NAME}' has been successfully initialized (no users created).")