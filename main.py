import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFileDialog, QPushButton, QLineEdit, \
    QTableWidget, QTableWidgetItem, QHBoxLayout

class SQLiteVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQLite Visualizer")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Top row for file selection
        self.file_selector_layout = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_selector_button = QPushButton("Select .db File")
        self.file_selector_button.clicked.connect(self.select_db_file)
        self.file_selector_layout.addWidget(self.file_path_input)
        self.file_selector_layout.addWidget(self.file_selector_button)
        self.layout.addLayout(self.file_selector_layout)

        # Second row for table operations and table view
        self.table_operations_layout = QHBoxLayout()
        
        # Table selector (thinner)
        self.table_selector = QTableWidget()
        self.table_selector.setColumnCount(1)
        self.table_selector.setHorizontalHeaderLabels([""])
        self.table_selector.itemClicked.connect(self.load_table_data)
        self.table_selector.setMaximumWidth(200)  # Set a maximum width to make it thinner
        
        # Table view
        self.table_view = QTableWidget()
        self.table_view.setEditTriggers(QTableWidget.DoubleClicked)
        self.table_view.cellChanged.connect(self.update_data)
        
        self.table_operations_layout.addWidget(self.table_selector)
        self.table_operations_layout.addWidget(self.table_view)
        self.layout.addLayout(self.table_operations_layout)

    def select_db_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select .db File", "", "SQLite Database Files (*.db);;All Files (*)", options=options)
        self.file_path_input.setText(file_path)
        self.connection = sqlite3.connect(file_path)
        self.cursor = self.connection.cursor()
        self.load_table_list()

    def load_table_list(self):
        self.table_selector.setRowCount(0)
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        for i, table in enumerate(tables):
            self.table_selector.insertRow(i)
            self.table_selector.setItem(i, 0, QTableWidgetItem(table[0]))

    def load_table_data(self, item):
        table_name = item.text()
        self.cursor.execute(f"SELECT * FROM {table_name};")
        data = self.cursor.fetchall()
        column_names = [description[0] for description in self.cursor.description]

        self.table_view.clear()
        self.table_view.setRowCount(len(data))
        self.table_view.setColumnCount(len(column_names))
        self.table_view.setHorizontalHeaderLabels(column_names)

        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                self.table_view.setItem(i, j, QTableWidgetItem(str(cell)))

    def update_data(self, row, column):
        table_name = self.table_selector.item(self.table_selector.currentRow(), 0).text()
        column_name = self.table_view.horizontalHeaderItem(column).text()
        new_value = self.table_view.item(row, column).text()
        self.cursor.execute(f"UPDATE {table_name} SET {column_name}=? WHERE rowid=?", (new_value, row + 1))
        self.connection.commit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SQLiteVisualizer()
    window.show()
    sys.exit(app.exec_())
