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

class DBManager(object):
    DB_NAME = 'transaction_categories.db'
    CATEGORIES_T = 'categories'
    TRANSACTIONS_T = 'transaction_categories'
    CATEGORY_K = 'category'
    IN_K = 'incoming'
    OUT_K = 'outcoming'

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.conn = sqlite3.connect(self.DB_NAME)
        self._create_tables()
        self._init_tables()

    def __del__(self):
        self.conn.close()

    def get_categories(self, incoming: bool) -> list[tuple[int, str]]:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT id, {self.CATEGORY_K} FROM {self.CATEGORIES_T} WHERE {self.IN_K} = (?)", (int(incoming),))
        return cursor.fetchall()

    def categorize(self, incoming: bool, description: str):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT {self.IN_K if incoming else self.OUT_K} FROM {self.TRANSACTIONS_T} WHERE saajan_nimi COLLATE NOCASE IN (?)", (description,))
        result = cursor.fetchone()
        if result:
            return int(result[0])
        return -1;

    def update_transaction_category(self, incoming: bool, description:str, category_id: int):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {self.TRANSACTIONS_T} WHERE saajan_nimi COLLATE NOCASE IN (?)", (description,))
        result = cursor.fetchone()
        if result:
            cursor.execute(f"UPDATE {self.TRANSACTIONS_T} SET {self.IN_K if incoming else self.OUT_K} = ? WHERE saajan_nimi COLLATE NOCASE IN (?)", (category_id, description,))
        else:
            cursor.execute(f"INSERT INTO {self.TRANSACTIONS_T} (saajan_nimi, {self.IN_K if incoming else self.OUT_K}) VALUES (?, ?)", (description, category_id))
        self.conn.commit()

    def get_category_by_id(self, category_id: int):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT {self.CATEGORY_K} FROM {self.CATEGORIES_T} WHERE id = ?", (category_id,))
        result = cursor.fetchone()
        return result[0] if result else ""

    def add_category(self, incoming: bool, name: str):
        pass

    def rename_category(self, incoming: bool, id: int, name: str):
        pass

    def remove_category(self, incoming: str, id: int):
        pass

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.CATEGORIES_T} (id INTEGER PRIMARY KEY, {self.CATEGORY_K} TEXT, {self.IN_K} INTEGER DEFAULT 0)")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.TRANSACTIONS_T} (saajan_nimi TEXT PRIMARY KEY, {self.IN_K} INTEGER, {self.OUT_K} INTEGER)")

    def _init_tables(self):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {self.CATEGORIES_T}")
        count = cursor.fetchone()[0]

        if count == 0:
            default_out_categories = [
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
            default_in_categories = [
                "Salary",
                "Interaccount transfer",
                "Direct transfer",
                "Debt returnal"
            ]

            for category in default_out_categories:
                cursor.execute(f"INSERT INTO {self.CATEGORIES_T} ({self.CATEGORY_K}) VALUES (?)", (category,))
            for category in default_in_categories:
                cursor.execute(f"INSERT INTO {self.CATEGORIES_T} ({self.CATEGORY_K}, {self.IN_K}) VALUES (?, ?)", (category, 1))
            self.conn.commit()


def parse_amount(amount_str: str) -> float:
    return float(amount_str.replace(",", "."))


def display_categories(db_manager: DBManager, incoming: bool) -> tuple[int]:
    categories = db_manager.get_categories(incoming)

    print(f"Available {'income categories' if incoming else 'outcome categories'}:")
    for cat_id, cat_name in categories:
        print(f"{cat_id}: {cat_name}")
    print("")
    return tuple(cat_id for cat_id, _ in categories)

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

def categorize_transaction(db_manager: DBManager, description: str, incoming: bool, transaction_info: dict[str, str]):
    result = db_manager.categorize(incoming, description)
    if result >= 0:
        category_id = result
    else:
        ids = display_categories(db_manager, incoming)
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
        if int_category_id not in ids:
            raise Exception("Invalid category ID")
        db_manager.update_transaction_category(incoming, description, int_category_id)
    return int(category_id)

def analyze_transactions(file_path: str, db_manager: DBManager):


    spent_categories = {}
    received_categories = {}

    spent_rows = db_manager.get_categories(False)
    received_rows = db_manager.get_categories(True)

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
            incoming = amount >= 0
            category_id = categorize_transaction(db_manager, description, incoming, transaction_info)

            if incoming:
                received_categories[category_id] += amount
            else:
                spent_categories[category_id] += abs(amount)

    return spent_categories, received_categories

def main():
    parser = argparse.ArgumentParser(description="Analyze and categorize bank transactions from a CSV file.")
    parser.add_argument("file_path", help="Path to the CSV file containing bank transactions.")
    args = parser.parse_args()

    db_manager = DBManager()

    spent_categories, received_categories = analyze_transactions(args.file_path, db_manager)

    print("Transaction Categorization and Analysis Report")
    print("---------------------------------------------")
    total_spent = 0
    total_received = 0

    print("Spent Categories:")
    for category_id, total in spent_categories.items():
        category_name = db_manager.get_category_by_id(category_id)
        print(f"{category_name}: {total:.2f} EUR")
        total_spent += total
    
    print("\nReceived Categories:")
    for category_id, total in received_categories.items():
        category_name = db_manager.get_category_by_id(category_id)
        print(f"{category_name}: {total:.2f} EUR")
        total_received += total

    print("---------------------------------------------")
    print(f"Total Spent: {total_spent:.2f} EUR")
    print(f"Total Received: {total_received:.2f} EUR")
    print("---------------------------------------------")

    # manage = input("Do you want to manage categories? (yes/no): ")
    # if manage.lower() == "yes":
        # manage_categories(conn, table_name)


if __name__ == "__main__":
    main()
