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
        cursor.execute(
            f"SELECT id, {self.CATEGORY_K} FROM {self.CATEGORIES_T} WHERE {self.IN_K} = (?)", (int(incoming),))
        return cursor.fetchall()

    def categorize(self, incoming: bool, description: str):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT {self.IN_K if incoming else self.OUT_K} FROM {self.TRANSACTIONS_T} WHERE saajan_nimi COLLATE NOCASE IN (?)", (description,))
        result = cursor.fetchone()
        if result and result[0]:
            return int(result[0])
        return -1

    def update_transaction_category(self, incoming: bool, description: str, category_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT * FROM {self.TRANSACTIONS_T} WHERE saajan_nimi COLLATE NOCASE IN (?)", (description,))
        result = cursor.fetchone()
        if result:
            cursor.execute(
                f"UPDATE {self.TRANSACTIONS_T} SET {self.IN_K if incoming else self.OUT_K} = ? WHERE saajan_nimi COLLATE NOCASE IN (?)", (category_id, description,))
        else:
            cursor.execute(
                f"INSERT INTO {self.TRANSACTIONS_T} (saajan_nimi, {self.IN_K if incoming else self.OUT_K}) VALUES (?, ?)", (description, category_id))
        self.conn.commit()

    def get_category_by_id(self, category_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT {self.CATEGORY_K} FROM {self.CATEGORIES_T} WHERE id = ?", (category_id,))
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
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {self.CATEGORIES_T} (id INTEGER PRIMARY KEY, {self.CATEGORY_K} TEXT, {self.IN_K} INTEGER DEFAULT 0)")
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {self.TRANSACTIONS_T} (saajan_nimi TEXT PRIMARY KEY, {self.IN_K} INTEGER, {self.OUT_K} INTEGER)")

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
                cursor.execute(
                    f"INSERT INTO {self.CATEGORIES_T} ({self.CATEGORY_K}) VALUES (?)", (category,))
            for category in default_in_categories:
                cursor.execute(
                    f"INSERT INTO {self.CATEGORIES_T} ({self.CATEGORY_K}, {self.IN_K}) VALUES (?, ?)", (category, 1))
            self.conn.commit()
