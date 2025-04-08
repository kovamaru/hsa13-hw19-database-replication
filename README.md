# hsa13-hw19-database-replication
Create mysql-m, mysql-s1, mysql-s2.  
Setup master slave replication.
Write script that will frequently write data to database.  
Ensure, that replication is working.  
Try to turn off mysql-s1 (stop slave).  Try to remove a column in  database on slave node (try to delete last column and column from the middle).  
Write conclusion in readme.md

## Setup
- Created 3 Docker containers: `mysql-m` (master), `mysql-s1` (slave), `mysql-s2` (slave).
- Configured master-slave replication with `mysql-m` as master and `mysql-s1`, `mysql-s2` as slaves using MySQL 9.2.0.
- Used `CHANGE REPLICATION SOURCE TO` and `sha256_password` plugin to handle authentication.

## Replication Check
- Wrote a Python script (`write_data.py`) to insert random user data into `test_db.users` every 5 seconds on `mysql-m`.
- Data successfully replicated to `mysql-s1` and `mysql-s2`, confirmed by querying `SELECT * FROM users`.

## Stopping Slave
- While the script `write_data.py` was inserting data every 5 seconds into `mysql-m`, I stopped replication on `mysql-s1` with `STOP REPLICA`.
- Checked `SHOW REPLICA STATUS\G`: `Replica_IO_Running: No`, `Replica_SQL_Running: No`. New records stopped appearing on `mysql-s1` (stayed at 36 records), while `mysql-s2` continued receiving updates (reached 43+ records).
- After executing `START REPLICA` on `mysql-s1`, it caught up with the master within seconds, syncing to position 17417 in `mysql-bin.000003`. The `users` table updated to 51 records, matching the master, and `Seconds_Behind_Source` returned to 0.

## Column Removal
1. **Removing last column (`age`)**:
    - On `mysql-s1`, executed `ALTER TABLE test_db.users DROP COLUMN age`.
    - Table structure changed to `id`, `name`, `email` (confirmed with `DESCRIBE users`).
    - Script `write_data.py` continued inserting records with 4 columns (`id`, `name`, `email`, `age`) on the master.
    - Unexpectedly, replication did not stop: `Replica_SQL_Running: Yes`, `Seconds_Behind_Source: 0`. New records appeared on `mysql-s1` without the `age` column (e.g., `Eve, eve99@example.com`).
    - MySQL 9.2.0 seems to ignore extra columns in the binlog if they are missing in the slave's table schema, allowing replication to continue.

2. **Removing middle column (`email`)**:
    - Restored the table to `id`, `name`, `email`, `age` and synced with the master.
    - Executed `ALTER TABLE test_db.users DROP COLUMN email` on `mysql-s1`.
    - Table structure changed to `id`, `name` (confirmed with `DESCRIBE users`).
    - Script continued inserting 4-column records on the master.
    - Replication remained active: `Replica_SQL_Running: Yes`, `Seconds_Behind_Source: 0`. New records appeared on `mysql-s1` with only `id` and `name` (e.g., `Charlie`, `Diana`).
    - Similar to the `age` test, MySQL 9.2.0 ignored the missing `email` and `age` columns and continued replication.

## Conclusion
- MySQL replication in version 9.2.0 behaves differently from older versions. Unlike the expected behavior where schema mismatches (e.g., dropping a column on a slave) break replication with a "Column count mismatch" error, here it adapts by discarding extra columns from the master's binlog entries. This allowed replication to continue seamlessly after dropping both the last column (`age`) and a middle column (`email`) on `mysql-s1`.
