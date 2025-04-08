import mysql.connector
import time
import random


db_config = {
  'host': 'localhost',
  'port': 3306,
  'user': 'root',
  'password': 'root',
  'database': 'test_db'
}

names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace']

def insert_data():
  try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    name = random.choice(names)
    email = f"{name.lower()}{random.randint(1, 100)}@example.com"
    age = random.randint(18, 60)
    cursor.execute("INSERT INTO users (name, email, age) VALUES (%s, %s, %s)", (name, email, age))
    conn.commit()
    print(f"Inserted: {name}, {email}, {age}")
    cursor.close()
    conn.close()
  except Exception as e:
    print(f"Error: {e}")

if __name__ == "__main__":
  while True:
    insert_data()
    time.sleep(5)