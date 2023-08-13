"""
Shows categories available
Different categories for expenses, incomes
More info when asks for category
total stats
edit categories
"""
import argparse
import csv
import sqlite3

DB_NAME = 'transaction_categories.db'
DB_CATIN_T = 'income_categories'
DB_CATOUT_T = 'outcome_categories'
DB_TRANSACTIONS_T = 'transaction_categories'

def parse_amount(amount_str):
    return float(amount_str.replace(",", "."))


def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {DB_CATIN_T} (id INTEGER PRIMARY KEY, category TEXT)")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {DB_CATOUT_T} (id INTEGER PRIMARY KEY, category TEXT)")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {DB_TRANSACTIONS_T} (saajan_nimi TEXT PRIMARY KEY, {DB_CATIN_T} INTEGER, {DB_CATOUT_T} INTEGER)")


def initialize_outcoming_categories_table(conn):
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {DB_CATOUT_T}")
    out_count = cursor.fetchone()[0]

    if out_count == 0:
        default_categories = [
            "Housing and Utilities",
            "Transportation",
            "Groceries",
            "Cafes & Restaurants",
            "Personal Care",
            "Healthcare",
            "Entertainment",
            "Debt Payments",
            "Savings and Investments",
            "Gifts and Donations",
            "Insurance",
            "Utilities",
            "Miscellaneous",
            "Uncategorized"
        ]

        for category in default_categories:
            cursor.execute(f"INSERT INTO {DB_CATOUT_T} (category) VALUES (?)", (category,))

        conn.commit()


def initialize_incoming_categories_table(conn):
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {DB_CATIN_T}")
    in_count = cursor.fetchone()[0]
    if in_count == 0:
        default_categories = [
            "Salary",
            "Interaccount transfer",
            "Direct transfer",
            "Debt returnal"
        ]

        for category in default_categories:
            cursor.execute(f"INSERT INTO {DB_CATIN_T} (category) VALUES (?)", (category,))

        conn.commit()


def display_categories(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    categories = cursor.fetchall()

    print(f"Available {table_name.replace('_', ' ')}:")
    for cat_id, cat_name in categories:
        print(f"{cat_id}: {cat_name}")
    print("")
    return len(categories)

def manage_categories(conn, table_name):
    while True:
        display_categories(conn, table_name)
        action = input("Enter 'add' to add a new category, 'rename' to rename an existing category, 'delete' to delete a category, or 'done' to finish: ")

        if action == "done":
            break

        if action == "add":
            new_category = input("Enter the name of the new category: ")
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {table_name} (category) VALUES (?)", (new_category,))
            conn.commit()
            print(f"{new_category} has been added.\n")

        elif action == "rename":
            cat_id = input("Enter the ID of the category to rename: ")
            new_name = input("Enter the new name for the category: ")
            cursor = conn.cursor()
            cursor.execute(f"UPDATE {table_name} SET category = ? WHERE id = ?", (new_name, cat_id))
            conn.commit()
            print(f"Category {cat_id} has been renamed to {new_name}.\n")

        elif action == "delete":
            cat_id = input("Enter the ID of the category to delete: ")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (cat_id,))
            conn.commit()
            print(f"Category {cat_id} has been deleted.\n")

def categorize_transaction(conn, description, table_name, transaction_info):
    cursor = conn.cursor()
    cursor.execute(f"SELECT {table_name} FROM {DB_TRANSACTIONS_T} WHERE saajan_nimi COLLATE NOCASE IN (?)", (description,))
    result = cursor.fetchone()

    if result:
        category_id = result[0]
    else:
        num = display_categories(conn, table_name)
        print("\nTransaction Details:")
        print("Maksupäivä:", transaction_info["Maksupäivä"])
        print("Summa:", transaction_info["Summa"])
        print("Tapahtumalaji:", transaction_info["Tapahtumalaji"])
        print("Maksaja:", transaction_info["Maksaja"])
        print("Saajan nimi:", transaction_info["Saajan nimi"])
        print("Viesti:", transaction_info["Viesti"])

        category_id = input("Please enter a category ID for this transaction: ")
        try:
            int_category_id = int(category_id)
        except ValueError:
            raise Exception("Invalid category ID")
        if int_category_id > num:
            raise Exception("Invalid category ID")

        cursor.execute(f"SELECT * FROM {DB_TRANSACTIONS_T} WHERE saajan_nimi COLLATE NOCASE IN (?)", (description,))
        result = cursor.fetchone()
        if result:
            cursor.execute(f"UPDATE {DB_TRANSACTIONS_T} SET {table_name} = ? WHERE saajan_nimi COLLATE NOCASE IN (?)", (category_id, description,))

        else:
            cursor.execute(f"INSERT INTO {DB_TRANSACTIONS_T} (saajan_nimi, {table_name}) VALUES (?, ?)", (description, category_id))
        conn.commit()
        
    return int(category_id)

def analyze_transactions(file_path, conn):
    create_tables(conn)
    initialize_outcoming_categories_table(conn)
    initialize_incoming_categories_table(conn)

    spent_categories = {}
    received_categories = {}

    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {DB_CATOUT_T}")
    spent_rows = cursor.fetchall()
    cursor.execute(f"SELECT * FROM {DB_CATIN_T}")
    received_rows = cursor.fetchall()

    for row in spent_rows:
        spent_categories[row[0]] = 0
    for row in received_rows:
        received_categories[row[0]] = 0

    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            amount = parse_amount(row['Summa'])
            description = row['Saajan nimi']
            transaction_info = {
                "Maksupäivä": row['Maksupäivä'],
                "Summa": row['Summa'],
                "Tapahtumalaji": row['Tapahtumalaji'],
                "Maksaja": row['Maksaja'],
                "Saajan nimi": description,
                "Viesti": row['Viesti']
            }
            table_name = DB_CATIN_T if amount >= 0 else DB_CATOUT_T
            category_id = categorize_transaction(conn, description, table_name, transaction_info)

            if amount < 0:
                spent_categories[category_id] += abs(amount)
            else:
                received_categories[category_id] += amount

    return spent_categories, received_categories

def main():
    parser = argparse.ArgumentParser(description="Analyze and categorize bank transactions from a CSV file.")
    parser.add_argument("file_path", help="Path to the CSV file containing bank transactions.")
    args = parser.parse_args()

    conn = sqlite3.connect("transaction_categories.db")
    
    spent_categories, received_categories = analyze_transactions(args.file_path, conn)

    print("Transaction Categorization and Analysis Report")
    print("---------------------------------------------")
    cursor = conn.cursor()
    total_spent = 0
    total_received = 0

    print("Spent Categories:")
    for category_id, total in spent_categories.items():
        cursor.execute(f"SELECT category FROM {DB_CATOUT_T} WHERE id = ?", (category_id,))
        category_name = cursor.fetchone()[0]
        print(f"{category_name}: {total:.2f} EUR")
        total_spent += total
    
    print("\nReceived Categories:")
    for category_id, total in received_categories.items():
        cursor.execute(f"SELECT category FROM {DB_CATIN_T} WHERE id = ?", (category_id,))
        category_name = cursor.fetchone()[0]
        print(f"{category_name}: {total:.2f} EUR")
        total_received += total

    print("---------------------------------------------")
    print(f"Total Spent: {total_spent:.2f} EUR")
    print(f"Total Received: {total_received:.2f} EUR")
    print("---------------------------------------------")

    manage = input("Do you want to manage categories? (yes/no): ")
    if manage.lower() == "yes":
        manage_categories(conn, table_name)

    conn.close()

if __name__ == "__main__":
    main()
