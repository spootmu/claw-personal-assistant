import sqlite3

print('=== FINAL DATABASE ANALYSIS ===')

# Check both database files
db_files = ['claw_data.db', 'learning_data.db']
for db_file in db_files:
    print(f'\n--- {db_file} ---')
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    
    for table in tables:
        if table not in ['sqlite_sequence']:  # Skip internal SQLite table
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f'{table}: {count} records')
            
            # Check for duplicates in each table
            if table == 'community_insights' and count > 0:
                cursor.execute('SELECT COUNT(DISTINCT insight) FROM community_insights')
                distinct_count = cursor.fetchone()[0]
                
                print(f'  Unique insights: {distinct_count}')
                
                if count > distinct_count:
                    print('  *** DUPLICATES STILL EXIST in community_insights ***')
                else:
                    print('  SUCCESS: No duplicates in community_insights!')
                    
            elif table == 'learnings' and count > 0:
                cursor.execute('SELECT COUNT(DISTINCT learning_content) FROM learnings')
                distinct_count = cursor.fetchone()[0]
                
                print(f'  Unique learning contents: {distinct_count}')
                
                if count > distinct_count:
                    print('  *** DUPLICATES EXIST in learnings ***')
                else:
                    print('  SUCCESS: No duplicates in learnings!')
    
    conn.close()

print('\n=== COMPREHENSIVE DUPLICATE CHECK ===')
conn1 = sqlite3.connect('claw_data.db')
conn2 = sqlite3.connect('learning_data.db')

c1, c2 = conn1.cursor(), conn2.cursor()

# Check claw_data.db
c1.execute('SELECT COUNT(*), COUNT(DISTINCT insight) FROM community_insights')
ci_total, ci_unique = c1.fetchone()
c1.execute('SELECT COUNT(*), COUNT(DISTINCT learning_content) FROM learnings')
l_total, l_unique = c1.fetchone()

# Check learning_data.db
c2.execute('SELECT COUNT(*), COUNT(DISTINCT learning_content) FROM learnings')
l2_total, l2_unique = c2.fetchone()

print(f'claw_data.db - Community Insights: {ci_total} total, {ci_unique} unique')
print(f'claw_data.db - Learnings: {l_total} total, {l_unique} unique')
print(f'learning_data.db - Learnings: {l2_total} total, {l2_unique} unique')

overall_total = ci_total + l_total + l2_total
overall_unique = ci_unique + l_unique + l2_unique

if overall_total > overall_unique:
    duplicate_count = overall_total - overall_unique
    print(f'\n*** {duplicate_count} DUPLICATES STILL EXIST IN THE SYSTEM ***')
else:
    print(f'\nSUCCESS: NO DUPLICATES FOUND IN THE ENTIRE SYSTEM!')
    print(f'Total records across all databases: {overall_total}')

conn1.close()
conn2.close()