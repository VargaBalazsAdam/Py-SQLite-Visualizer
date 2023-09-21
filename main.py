import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFileDialog, QPushButton, QLineEdit, \
    QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView, QMenu, QTextEdit, QLabel, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt

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

        # Set the horizontal size policy to expanding
        table_selector_header = self.table_selector.horizontalHeader()
        table_selector_header.setSectionResizeMode(QHeaderView.Stretch)

        # Create context menu for right-click actions
        self.table_selector.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_selector.customContextMenuRequested.connect(self.show_context_menu)

        # Table view
        self.table_view = QTableWidget()
        self.table_view.setEditTriggers(QTableWidget.DoubleClicked)
        self.table_view.cellChanged.connect(self.update_data)

        self.table_operations_layout.addWidget(self.table_selector)
        self.table_operations_layout.addWidget(self.table_view)
        self.layout.addLayout(self.table_operations_layout)

        # Context menu
        self.context_menu = QMenu(self)
        self.delete_table_action = self.context_menu.addAction("Delete Table")
        self.delete_table_action.triggered.connect(self.delete_table)

        # Create table button and editor
        self.create_table_button = QPushButton("Create Table")
        self.create_table_button.clicked.connect(self.show_table_creator)
        self.layout.addWidget(self.create_table_button)

        # Create table creator widgets (initially hidden)
        self.table_creator_layout = QVBoxLayout()
        self.table_creator_layout.setSpacing(10)
        self.table_name_input = QLineEdit()
        self.table_sql_input = QTextEdit()
        self.table_create_button = QPushButton("Create")
        self.table_create_button.clicked.connect(self.create_table)
        self.table_cancel_button = QPushButton("Cancel")
        self.table_cancel_button.clicked.connect(self.cancel_table_creation)
        self.table_creator_layout.addWidget(QLabel("Table Name:"))
        self.table_creator_layout.addWidget(self.table_name_input)
        self.table_creator_layout.addWidget(QLabel("Table SQL:"))
        self.table_creator_layout.addWidget(self.table_sql_input)
        self.table_creator_layout.addWidget(self.table_create_button)
        self.table_creator_layout.addWidget(self.table_cancel_button)
        self.layout.addLayout(self.table_creator_layout)
        self.hide_table_creator()

        # Flag to track whether in table viewing or creating mode
        self.viewing_mode = True

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

    def show_context_menu(self, position):
        if self.table_selector.itemAt(position):
            self.context_menu.exec_(self.table_selector.mapToGlobal(position))

    def delete_table(self):
        if self.table_selector.currentItem():
            table_name = self.table_selector.currentItem().text()
            confirm = QMessageBox.question(self, "Delete Table", f"Are you sure you want to delete table '{table_name}'?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.cursor.execute(f"DROP TABLE {table_name};")
                self.connection.commit()
                self.load_table_list()

    def show_table_creator(self):
        if self.viewing_mode:
            self.hide_table_viewer_widgets()
            self.show_table_creator_widgets()
            self.viewing_mode = False

    def hide_table_creator(self):
        self.table_name_input.clear()
        self.table_sql_input.clear()
        for i in reversed(range(self.table_creator_layout.count())):
            widget = self.table_creator_layout.itemAt(i).widget()
            if widget is not None:
                widget.hide()  # Hide individual widgets

    def show_table_creator_widgets(self):
        self.table_name_input.clear()
        self.table_sql_input.clear()
        for i in range(self.table_creator_layout.count()):
            widget = self.table_creator_layout.itemAt(i).widget()
            if widget is not None:
                widget.show()  # Show individual widgets

    def hide_table_viewer_widgets(self):
        self.table_selector.hide()
        self.table_view.hide()
        self.create_table_button.hide()

    def show_table_viewer_widgets(self):
        self.table_selector.show()
        self.table_view.show()
        self.create_table_button.show()

    def create_table(self):
        table_name = self.table_name_input.text()
        table_sql = self.table_sql_input.toPlainText()

        if table_name and table_sql:
            try:
                self.cursor.execute(table_sql)
                self.connection.commit()
                self.load_table_list()
                self.hide_table_creator()
                self.show_table_viewer_widgets()
                self.viewing_mode = True
            except Exception as e:
                QMessageBox.critical(self, "Error Creating Table", str(e))
        else:
            QMessageBox.warning(self, "Missing Information", "Please enter both a table name and SQL.")

    def cancel_table_creation(self):
        self.hide_table_creator()
        self.show_table_viewer_widgets()
        self.viewing_mode = True

    def add_row(self):
        self.table_view.insertRow(self.table_view.rowCount())

    def delete_row(self):
        current_row = self.table_view.currentRow()
        if current_row >= 0:
            self.table_view.removeRow(current_row)

    def change_column_name(self):
        current_column = self.table_view.currentColumn()
        if current_column >= 0:
            new_name, ok = QInputDialog.getText(self, "Change Column Name", "New Column Name:")
            if ok and new_name:
                self.table_view.horizontalHeaderItem(current_column).setText(new_name)

    def change_column_type(self):
        current_column = self.table_view.currentColumn()
        if current_column >= 0:
            new_type, ok = QInputDialog.getText(self, "Change Column Type", "New Column Type:")
            if ok and new_type:
                self.table_view.horizontalHeaderItem(current_column).setText(new_type)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SQLiteVisualizer()
    window.show()
    sys.exit(app.exec_())
