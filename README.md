# Py-SQLite-Visualizer

SQLite Visualizer is a simple desktop application built using PyQt5 that allows you to interact with SQLite databases. With this tool, you can:

-    Open and select existing SQLite database files.
-    Create new empty SQLite databases.
-    View and edit the tables and data within a selected database.
-    Create new tables with custom SQL queries.
-    Delete tables and rows.
-    Save changes made to the database.

## Getting Started

### Prerequisites
Before you can run this application, you need to have Python and PyQt5 installed on your system. You also need the `sqlite3` library, which is usually included with Python.

### Installation
1. Clone the repository to your local machine.
```bash
git clone https://github.com/VargaBalazsAdam/Py-SQLite-Visualizer.git
```
2. Change to the project directory.
```bash
cd sqlite-visualizer
```
3. Run the application.
```bash
python main.py
```

## How To Use

### Select an Existing Database:
- Click the "Select .db File" button to open a file dialog.
- Choose an existing SQLite database (.db file) to load.
- The tables in the selected database will be displayed in the left panel. Click on a table to view its data.

### Create a New Empty Database:
- Click the "Create Empty Database" button to create a new, empty SQLite database.
- The new database will be automatically selected and loaded.

### Table Operations:
- To create a new table, click the "Create Table" button and provide the SQL query for table creation. Click "Create" to create the table.
- To delete a table, right-click on the table name in the left panel and select "Delete Table."
- To edit a table, double-click on a cell in the table view and make your changes. Press Enter to save the changes.

### Row Operations:
- To add a new row to a table, simply right-click anywhere within the table view's empty area.
- To delete a row, right-click on a row in the table view and select "Delete Row."

### Save Changes:
- Press `Ctrl + S` to save changes made to the database.