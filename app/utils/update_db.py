# update_db.py

import mysql.connector
from mysql.connector import Error
from app.config import Config
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random


def execute_sql_file(connection, sql_file):
    try:
        with open(sql_file, 'r') as file:
            sql_script = file.read()

        cursor = connection.cursor()

        # Split the SQL script into individual statements
        statements = sql_script.split(';')

        for statement in statements:
            if statement.strip():
                cursor.execute(statement)

        connection.commit()
        print("SQL script executed successfully")
    except Error as e:
        print(f"Error executing SQL script: {e}")
    finally:
        if cursor:
            cursor.close()


def create_admin_user(connection):
    try:
        cursor = connection.cursor()
        admin_username = "admin"
        admin_email = "admin@example.com"
        admin_password = "admin_password"  # Change this to a secure password
        hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')

        cursor.execute("""
            INSERT INTO users (username, email, password_hash, is_admin)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            email = VALUES(email),
            password_hash = VALUES(password_hash),
            is_admin = VALUES(is_admin)
        """, (admin_username, admin_email, hashed_password, True))

        connection.commit()
        print("Admin user created or updated successfully")
    except Error as e:
        print(f"Error creating admin user: {e}")
    finally:
        if cursor:
            cursor.close()


def create_mock_data(connection):
    try:
        cursor = connection.cursor()

        # Create mock users
        users = [
            ("user1", "user1@example.com", "password1"),
            ("user2", "user2@example.com", "password2"),
            ("user3", "user3@example.com", "password3")
        ]

        user_ids = []
        for username, email, password in users:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, is_admin)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                email = VALUES(email),
                password_hash = VALUES(password_hash)
            """, (username, email, hashed_password, False))
            user_ids.append(cursor.lastrowid)

        # Create mock categories
        categories_ids = []
        cursor.execute("""
                        INSERT INTO categories (name) VALUES
                        ('CATEGORY ONE'),
                        ('CATEGORY TWO');
                    """)
        categories_ids.append(cursor.lastrowid)

        # Create mock products
        products = [
            ('BANANAS', 'YUMMMMM', 1000.00, 1),
            ('COCONUTS', 'THESE ARE ALL FOR THE WATER', 500.00, 1),
            ('SOME OTHER SHIT', 'THIS EXPENSIVE YALL', 1000000.00, 2)
        ]

        product_ids = []
        for name, description, price, category_id in products:
            cursor.execute("""
                INSERT INTO products (name, description, price, category_id)
                VALUES (%s, %s, %s, %s)
            """, (name, description, price, category_id))
            product_ids.append(cursor.lastrowid)

        # Create mock orders and order items
        statuses = ["Processing", "Shipped", "Delivered", "Cancelled"]

        for _ in range(10):  # Create 10 orders
            user_id = random.choice(user_ids)
            status = random.choice(statuses)
            order_date = datetime.now() - timedelta(days=random.randint(1, 30))

            cursor.execute("""
                INSERT INTO orders (user_id, status, total_price, created_at)
                VALUES (%s, %s, %s, %s)
            """, (user_id, status, 0, order_date))
            order_id = cursor.lastrowid

            total_price = 0
            for _ in range(random.randint(1, 3)):  # 1 to 3 items per order
                product_id = random.choice(product_ids)
                quantity = random.randint(1, 5)

                cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
                price = cursor.fetchone()[0]

                item_total = price * quantity
                total_price += item_total

                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, product_id, quantity, price))

            # Update the total price of the order
            cursor.execute("UPDATE orders SET total_price = %s WHERE id = %s", (total_price, order_id))

        connection.commit()
        print("Mock data created successfully")
    except Error as e:
        print(f"Error creating mock data: {e}")
    finally:
        if cursor:
            cursor.close()


def main():
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )

        if connection.is_connected():
            print("Connected to MySQL database")
            execute_sql_file(connection, 'schema.sql')
            create_admin_user(connection)
            create_mock_data(connection)
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection closed")


if __name__ == "__main__":
    main()
