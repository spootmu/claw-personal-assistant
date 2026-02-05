import sqlite3

# Check learning_data.db specifically since that's where the learnings table should be
conn = sqlite3.connect('learning_data.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [table[0] for table in cursor.fetchall()]
print('Tables in learning_data.db:', tables)

if 'learnings' in tables:
    cursor.execute('SELECT COUNT(*) FROM learnings')
    total_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(DISTINCT learning_content) FROM learnings')
    distinct_count = cursor.fetchone()[0]
    
    print(f'Total records: {total_count}')
    print(f'Distinct records: {distinct_count}')
    
    if total_count > distinct_count:
        print('There are still duplicate records.')
        cursor.execute('SELECT learning_content, COUNT(*) FROM learnings GROUP BY learning_content HAVING COUNT(*) > 1 LIMIT 5')
        duplicates = cursor.fetchall()
        print('Sample duplicates:')
        for dup in duplicates:
            print(f'  {dup[1]}x: {dup[0][:80]}...')
    else:
        print('SUCCESS: No duplicates found in learnings table!')
        
conn.close()