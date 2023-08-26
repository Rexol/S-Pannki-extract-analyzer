import csv
import io


class InputFileManager:
    def __init__(self, file_path: str, output_path: str):
        self.file_path = file_path
        self.output_path = output_path
        self.in_file = None
        self.out_file = None
        self.categorized = False
        self.curr = {}

    def __enter__(self):
        self.in_file = io.open(self.file_path, 'r', encoding='utf-8')
        self.out_file = io.open(self.output_path, 'w',
                                encoding='utf-8', newline='')

        self.reader = csv.DictReader(self.in_file, delimiter=';')
        fieldnames = list(self.reader.fieldnames)  # type: ignore
        extended_fieldnames = fieldnames + ['incoming', 'category']
        self.writer = csv.DictWriter(
            self.out_file, delimiter=';', fieldnames=extended_fieldnames)
        self.writer.writeheader()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.in_file.close()  # type: ignore
        self.out_file.close()  # type: ignore

    def rows(self):
        for row in self.reader:
            self.curr = row
            yield row

    def get_current_row(self):
        return self.curr

    def categoruze_current_row(self, incoming: bool, category: str):
        self.categorized = True
        self.curr['incoming'] = 1 if incoming else 0
        self.curr['category'] = category

    def write_current_row(self):
        if not self.categorized:
            self.categoruze_current_row(False, "uncategorized")
        self.writer.writerow(self.curr)
