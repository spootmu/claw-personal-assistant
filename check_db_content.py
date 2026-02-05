import sqlite3
import os

# Check both database files
db_files = [f for f in os.listdir('.') if f.endswith('.db')]
for db_file in db_files:
    print(f'\n=== Checking {db_file} ===')
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    print(f'Tables in {db_file}: {tables}')
    
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'{table}: {count} records')
        
        if table == 'learnings' and count > 0:
            cursor.execute('SELECT COUNT(DISTINCT learning_content) FROM learnings')
            distinct_count = cursor.fetchone()[0]
            
            print(f'  Total records: {count}')
            print(f'  Distinct records: {distinct_count}')
            
            if count > distinct_count:
                print('  There are duplicate records in the learnings table.')
                cursor.execute('SELECT learning_content, COUNT(*) FROM learnings GROUP BY learning_content HAVING COUNT(*) > 1 LIMIT 5')
                duplicates = cursor.fetchall()
                print('  Sample duplicates:')
                for dup in duplicates:
                    print(f'    {dup[1]}x: {dup[0][:80]}...')
            else:
                print('  SUCCESS: No duplicates found in learnings table!')
        
        # If there are records, show a sample
        if count > 0 and table != 'sqlite_sequence':
            cursor.execute(f'SELECT * FROM {table} LIMIT 3')
            samples = cursor.fetchall()
            if samples:
                print(f'  Sample records:')
                for i, sample in enumerate(samples):
                    print(f'    {i+1}: {sample}')
                
    conn.close()