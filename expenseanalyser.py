import argparse
from file_manager import InputFileManager
from db_manager import DBManager


def parse_amount(amount_str: str) -> float:
    return float(amount_str.replace(",", "."))


def display_categories(db_manager: DBManager, incoming: bool) -> tuple[int]:
    categories = db_manager.get_categories(incoming)

    print(
        f"Available {'income categories' if incoming else 'outcome categories'}:")
    for cat_id, cat_name in categories:
        print(f"{cat_id}: {cat_name}")
    print("")
    return tuple(cat_id for cat_id, _ in categories)


def manage_categories(conn, table_name):
    while True:
        display_categories(conn, table_name)
        action = input(
            "Enter 'add' to add a new category, 'rename' to rename an existing category, 'delete' to delete a category, or 'done' to finish: ")

        if action == "done":
            break

        if action == "add":
            new_category = input("Enter the name of the new category: ")
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO {table_name} (category) VALUES (?)", (new_category,))
            conn.commit()
            print(f"{new_category} has been added.\n")

        elif action == "rename":
            cat_id = input("Enter the ID of the category to rename: ")
            new_name = input("Enter the new name for the category: ")
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {table_name} SET category = ? WHERE id = ?", (new_name, cat_id))
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

        category_id = input(
            "Please enter a category ID for this transaction: ")
        try:
            int_category_id = int(category_id)
        except ValueError:
            raise Exception("Invalid category ID")
        if int_category_id not in ids:
            raise Exception("Invalid category ID")
        db_manager.update_transaction_category(
            incoming, description, int_category_id)
    return int(category_id)


def analyze_transactions(file_manager: InputFileManager, db_manager: DBManager):
    spent_categories = {}
    received_categories = {}

    spent_rows = db_manager.get_categories(False)
    received_rows = db_manager.get_categories(True)

    for row in spent_rows:
        spent_categories[row[0]] = 0
    for row in received_rows:
        received_categories[row[0]] = 0

    for row in file_manager.rows():
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
        category_id = categorize_transaction(
            db_manager, description, incoming, transaction_info)

        file_manager.categoruze_current_row(
            incoming, db_manager.get_category_by_id(category_id))
        file_manager.write_current_row()
        if incoming:
            received_categories[category_id] += amount
        else:
            spent_categories[category_id] += abs(amount)

    return spent_categories, received_categories


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and categorize bank transactions from a CSV file.")
    parser.add_argument(
        "file_path", help="Path to the CSV file containing bank transactions.")
    parser.add_argument(
        "-o", "--output", help="Path to the output CSV file.", default="out.csv")
    args = parser.parse_args()

    db_manager = DBManager()

    with InputFileManager(args.file_path, args.output) as file_manager:
        spent_categories, received_categories = analyze_transactions(
            file_manager, db_manager)

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
