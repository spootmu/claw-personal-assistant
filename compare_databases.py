import sqlite3

# Check both database files
db_files = ['claw_data.db', 'learning_data.db']

for db_file in db_files:
    print(f'\n=== Checking {db_file} ===')
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    print(f'Tables in {db_file}: {tables}')

    for table in tables:
        print(f'\nStructure of {table} in {db_file}:')
        cursor.execute(f'PRAGMA table_info({table})')
        columns = cursor.fetchall()
        for col in columns:
            print(f'  {col[1]} ({col[2]}) - {col[5] and "PRIMARY KEY" or ""} {col[3] and "NOT NULL" or ""}')

    conn.close()