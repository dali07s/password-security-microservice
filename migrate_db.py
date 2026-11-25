import sqlite3

connection = sqlite3.connect("password_security.db")

columns = [
    row[1]
    for row in connection.execute(
        "PRAGMA table_info(totp_accounts)"
    )
]

if "last_used_step" not in columns:
    connection.execute(
        "ALTER TABLE totp_accounts ADD COLUMN last_used_step INTEGER"
    )
    connection.commit()
    print("Migration completed")

else:
    print("Column already exists")

connection.close()