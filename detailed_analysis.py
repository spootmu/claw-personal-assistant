import sqlite3

print('=== DETAILED DATABASE ANALYSIS ===')

# Check both database files
db_files = ['claw_data.db', 'learning_data.db']
total_learnings = 0
distinct_learnings = 0

for db_file in db_files:
    print(f'\n--- {db_file} ---')
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    
    for table in tables:
        if table != 'sqlite_sequence':  # Skip internal SQLite table
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f'{table}: {count} records')
            
            if count > 0 and table == 'learnings':
                # Get all learning records for duplicate analysis
                cursor.execute(f'SELECT * FROM {table}')
                records = cursor.fetchall()
                
                print(f'  LEARNING RECORDS ANALYSIS:')
                if len(records) > 0:
                    # Extract learning content (assuming it's at index 2 - after id and timestamp)
                    content_list = []
                    for record in records:
                        if len(record) > 2:  # Make sure the record has enough fields
                            content_list.append(record[2])  # learning_content is typically at index 2
                    
                    unique_contents = set(content_list)
                    
                    print(f'    Total records: {len(content_list)}')
                    print(f'    Unique contents: {len(unique_contents)}')
                    
                    total_learnings += len(content_list)
                    distinct_learnings += len(unique_contents)
                    
                    if len(content_list) > len(unique_contents):
                        print('    *** DUPLICATES DETECTED ***')
                        # Find and report duplicates
                        seen = set()
                        duplicates = []
                        for i, content in enumerate(content_list):
                            if content in seen:
                                duplicates.append((i, content))
                            else:
                                seen.add(content)
                        
                        if duplicates:
                            print(f'    Number of duplicate entries: {len(duplicates)}')
                            for idx, content in duplicates[:5]:  # Show first 5 duplicates
                                print(f'      Duplicate: {content[:60]}...')
                    else:
                        print('    No duplicates found in this table - OPTIMIZATION SUCCESSFUL!')
                else:
                    print('    No learning records found')
            elif table == 'community_insights':
                print(f'  COMMUNITY INSIGHTS SAMPLE (first 3):')
                cursor.execute(f'SELECT * FROM {table} LIMIT 3')
                records = cursor.fetchall()
                for i, record in enumerate(records):
                    if len(record) >= 4:
                        print(f'    {i+1}: Topic="{record[3][:50]}..." from {record[2]}')
    
    conn.close()

print(f'\n=== FINAL SUMMARY ===')
print(f'Total learning records across all databases: {total_learnings}')
print(f'Distinct learning contents across all databases: {distinct_learnings}')

if total_learnings > 0:
    if total_learnings > distinct_learnings:
        duplicate_count = total_learnings - distinct_learnings
        print(f'*** {duplicate_count} DUPLICATE RECORDS FOUND IN SYSTEM ***')
        print('Optimization was NOT fully successful.')
    else:
        print('SUCCESS: No duplicates found in the entire system!')
        print('Optimization was successful!')
else:
    print('No learning records generated yet, but no duplicates either.')
    print('The system is clean and ready to generate unique learning records.')