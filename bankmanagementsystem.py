import sqlite3
conn=sqlite3.connect("banckmanagement.db")
cursor=conn.cursor()

cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer'
        )
    """)

cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_number TEXT UNIQUE NOT NULL,
            account_type TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
            ON DELETE CASCADE
        )
    """)

cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            transaction_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
            ON DELETE CASCADE
        )
    """)

cursor.execute("""
        INSERT OR IGNORE INTO users
        (username, password, name, email, phone, role)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "admin",
        "admin123",
        "Administrator",
        "admin@bank.com",
        "9999999999",
        "admin"
    ))

conn.commit()
conn.close()


# ==========================================
# ACCOUNT NUMBER
# ==========================================

def generate_account_number():
    conn=sqlite3.connect("banckmanagement.db")
    cursor=conn.cursor()

    cursor.execute("""
        SELECT account_number
        FROM accounts
        ORDER BY account_id DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()

    if result is None:
        return "100001"

    return str(int(result[0]) + 1)


# ==========================================
# CUSTOMER REGISTRATION
# ==========================================

def register():
    print("\n========== CUSTOMER REGISTRATION ==========")

    name = input("Enter name: ").strip()
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    email = input("Enter email: ").strip()
    phone = input("Enter phone: ").strip()

    if not name or not username or not password or not email or not phone:
        print("All fields are required.")
        return

    conn=sqlite3.connect("banckmanagement.db")
    cursor=conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users
            (username, password, name, email, phone, role)
            VALUES (?, ?, ?, ?, ?, 'customer')
        """, (username, password, name, email, phone))

        user_id = cursor.lastrowid

        account_number = generate_account_number()

        cursor.execute("""
            INSERT INTO accounts
            (user_id, account_number, account_type, balance)
            VALUES (?, ?, ?, ?)
        """, (user_id, account_number, "Savings", 0))

        conn.commit()

        print("\nRegistration successful!")
        print("Your Account Number:", account_number)

    except sqlite3.IntegrityError:
        conn.rollback()
        print("Username or email already exists.")

    except Exception as e:
        conn.rollback()
        print("Error:", e)

    finally:
        conn.close()


# ==========================================
# LOGIN
# ==========================================

def login():
    print("\n========== LOGIN ==========")

    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    if not username or not password:
        print("Username and password are required.")
        return None

    conn=sqlite3.connect("banckmanagement.db")
    cursor=conn.cursor()

    try:
        cursor.execute("""
            SELECT user_id, username, name, role
            FROM users
            WHERE username = ? AND password = ?
        """, (username, password))

        user = cursor.fetchone()

        if user:
            print("\nLogin successful!")
            print("Welcome", user[2])

            return {
                "user_id": user[0],
                "username": user[1],
                "name": user[2],
                "role": user[3]
            }

        print("Invalid username or password.")
        return None

    except Exception as e:
        print("Login error:", e)
        return None

    finally:
        conn.close()


# ==========================================
# CUSTOMER - ACCOUNT DETAILS
# ==========================================

def account_details(user_id):
    conn=sqlite3.connect("banckmanagement.db")
    cursor=conn.cursor()

    try:
        cursor.execute("""
            SELECT u.name,
                   u.email,
                   u.phone,
                   a.account_number,
                   a.account_type,
                   a.balance
            FROM users u
            JOIN accounts a
            ON u.user_id = a.user_id
            WHERE u.user_id = ?
        """, (user_id,))

        account = cursor.fetchone()

        if account:
            print("\n========== ACCOUNT DETAILS ==========")
            print("Name           :", account[0])
            print("Email          :", account[1])
            print("Phone          :", account[2])
            print("Account Number :", account[3])
            print("Account Type   :", account[4])
            print("Balance        :", account[5])

        else:
            print("Account not found.")

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()


# ==========================================
# DEPOSIT
# ==========================================

def deposit(user_id):
    print("\n========== DEPOSIT ==========")

    try:
        amount = float(input("Enter amount: "))

        if amount <= 0:
            print("Amount must be greater than 0.")
            return

        conn=sqlite3.connect("banckmanagement.db")
        cursor=conn.cursor()

        cursor.execute("""
            SELECT account_id
            FROM accounts
            WHERE user_id = ?
        """, (user_id,))

        account = cursor.fetchone()

        if not account:
            print("Account not found.")
            conn.close()
            return

        account_id = account[0]

        cursor.execute("""
            UPDATE accounts
            SET balance = balance + ?
            WHERE account_id = ?
        """, (amount, account_id))

        cursor.execute("""
            INSERT INTO transactions
            (account_id, transaction_type, amount, description)
            VALUES (?, ?, ?, ?)
        """, (
            account_id,
            "Deposit",
            amount,
            "Money deposited"
        ))

        conn.commit()

        print("Deposit successful.")

    except ValueError:
        print("Please enter a valid amount.")

    except Exception as e:
        print("Deposit failed:", e)

    finally:
        try:
            conn.close()
        except:
            pass


# ==========================================
# WITHDRAW
# ==========================================

def withdraw(user_id):
    print("\n========== WITHDRAW ==========")

    try:
        amount = float(input("Enter amount: "))

        if amount <= 0:
            print("Amount must be greater than 0.")
            return

        conn=sqlite3.connect("banckmanagement.db")
        cursor=conn.cursor()

        cursor.execute("""
            SELECT account_id, balance
            FROM accounts
            WHERE user_id = ?
        """, (user_id,))

        account = cursor.fetchone()

        if not account:
            print("Account not found.")
            conn.close()
            return

        account_id = account[0]
        balance = account[1]

        if amount > balance:
            print("Insufficient balance.")
            conn.close()
            return

        cursor.execute("""
            UPDATE accounts
            SET balance = balance - ?
            WHERE account_id = ?
        """, (amount, account_id))

        cursor.execute("""
            INSERT INTO transactions
            (account_id, transaction_type, amount, description)
            VALUES (?, ?, ?, ?)
        """, (
            account_id,
            "Withdraw",
            amount,
            "Money withdrawn"
        ))

        conn.commit()

        print("Withdrawal successful.")

    except ValueError:
        print("Please enter a valid amount.")

    except Exception as e:
        print("Withdrawal failed:", e)

    finally:
        try:
            conn.close()
        except:
            pass


# ==========================================
# CUSTOMER TRANSACTION HISTORY
# ==========================================

def transaction_history(user_id):
    conn=sqlite3.connect("banckmanagement.db")
    cursor=conn.cursor()

    try:
        cursor.execute("""
            SELECT t.transaction_id,
                   t.transaction_type,
                   t.amount,
                   t.description,
                   t.transaction_date
            FROM transactions t
            JOIN accounts a
            ON t.account_id = a.account_id
            WHERE a.user_id = ?
            ORDER BY t.transaction_id DESC
        """, (user_id,))

        transactions = cursor.fetchall()

        print("\n========== TRANSACTION HISTORY ==========")

        if not transactions:
            print("No transactions found.")
            return

        for transaction in transactions:
            print("------------------------------------------")
            print("Transaction ID :", transaction[0])
            print("Type           :", transaction[1])
            print("Amount         :", transaction[2])
            print("Description    :", transaction[3])
            print("Date           :", transaction[4])

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()


# ==========================================
# ADMIN - VIEW CUSTOMERS
# ==========================================

def view_customers():
    conn=sqlite3.connect("banckmanagement.db")
    cursor=conn.cursor()

    try:
        cursor.execute("""
            SELECT user_id, username, name, email, phone
            FROM users
            WHERE role = 'customer'
            ORDER BY user_id
        """)

        customers = cursor.fetchall()

        print("\n========== ALL CUSTOMERS ==========")

        if not customers:
            print("No customers found.")
            return

        for customer in customers:
            print("------------------------------------------")
            print("ID       :", customer[0])
            print("Username :", customer[1])
            print("Name     :", customer[2])
            print("Email    :", customer[3])
            print("Phone    :", customer[4])

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()


# ==========================================
# ADMIN - VIEW ALL ACCOUNTS
# ==========================================

def view_accounts():
    conn=sqlite3.connect("banckmanagement.db")
    cursor=conn.cursor()

    try:
        cursor.execute("""
            SELECT a.account_id,
                   u.name,
                   a.account_number,
                   a.account_type,
                   a.balance
            FROM accounts a
            JOIN users u
            ON a.user_id = u.user_id
            ORDER BY a.account_id
        """)

        accounts = cursor.fetchall()

        print("\n========== ALL ACCOUNTS ==========")

        if not accounts:
            print("No accounts found.")
            return

        for account in accounts:
            print("------------------------------------------")
            print("Account ID     :", account[0])
            print("Customer Name  :", account[1])
            print("Account Number :", account[2])
            print("Account Type   :", account[3])
            print("Balance        :", account[4])

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()


# ==========================================
# ADMIN - VIEW ALL TRANSACTIONS
# ==========================================

def view_all_transactions():
    conn=sqlite3.connect("banckmanagement.db")
    cursor=conn.cursor()

    try:
        cursor.execute("""
            SELECT t.transaction_id,
                   u.name,
                   a.account_number,
                   t.transaction_type,
                   t.amount,
                   t.transaction_date
            FROM transactions t
            JOIN accounts a
            ON t.account_id = a.account_id
            JOIN users u
            ON a.user_id = u.user_id
            ORDER BY t.transaction_id DESC
        """)

        transactions = cursor.fetchall()

        print("\n========== ALL TRANSACTIONS ==========")

        if not transactions:
            print("No transactions found.")
            return

        for transaction in transactions:
            print("------------------------------------------")
            print("Transaction ID :", transaction[0])
            print("Customer       :", transaction[1])
            print("Account Number :", transaction[2])
            print("Type           :", transaction[3])
            print("Amount         :", transaction[4])
            print("Date           :", transaction[5])

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()


# ==========================================
# ADMIN - UPDATE CUSTOMER
# ==========================================

def update_customer():
    print("\n========== UPDATE CUSTOMER ==========")

    try:
        user_id = int(input("Enter customer ID: "))

        conn=sqlite3.connect("banckmanagement.db")
        cursor=conn.cursor()

        cursor.execute("""
            SELECT name, email, phone
            FROM users
            WHERE user_id = ? AND role = 'customer'
        """, (user_id,))

        customer = cursor.fetchone()

        if not customer:
            print("Customer not found.")
            conn.close()
            return

        print("Current Name :", customer[0])
        print("Current Email:", customer[1])
        print("Current Phone:", customer[2])

        name = input("Enter new name: ").strip()
        email = input("Enter new email: ").strip()
        phone = input("Enter new phone: ").strip()

        if not name or not email or not phone:
            print("All fields are required.")
            conn.close()
            return

        cursor.execute("""
            UPDATE users
            SET name = ?, email = ?, phone = ?
            WHERE user_id = ?
        """, (name, email, phone, user_id))

        conn.commit()

        print("Customer updated successfully.")

    except ValueError:
        print("Customer ID must be a number.")

    except sqlite3.IntegrityError:
        print("Email already exists.")

    except Exception as e:
        print("Update failed:", e)

    finally:
        try:
            conn.close()
        except:
            pass


# ==========================================
# ADMIN - DELETE CUSTOMER
# ==========================================

def delete_customer():
    print("\n========== DELETE CUSTOMER ==========")

    try:
        user_id = int(input("Enter customer ID: "))

        conn=sqlite3.connect("banckmanagement.db")
        cursor=conn.cursor()

        cursor.execute("""
            SELECT name
            FROM users
            WHERE user_id = ? AND role = 'customer'
        """, (user_id,))

        customer = cursor.fetchone()

        if not customer:
            print("Customer not found.")
            conn.close()
            return

        print("Customer:", customer[0])

        confirm = input("Are you sure? (yes/no): ").lower()

        if confirm == "yes":
            cursor.execute("""
                DELETE FROM users
                WHERE user_id = ? AND role = 'customer'
            """, (user_id,))

            conn.commit()

            print("Customer deleted successfully.")

        else:
            print("Delete cancelled.")

    except ValueError:
        print("Customer ID must be a number.")

    except Exception as e:
        print("Delete failed:", e)

    finally:
        try:
            conn.close()
        except:
            pass


# ==========================================
# CUSTOMER MENU
# ==========================================

def customer_menu(user):
    while True:
        print("\n================================")
        print("         CUSTOMER MENU")
        print("================================")
        print("1. View Account Details")
        print("2. Check Balance")
        print("3. Deposit Money")
        print("4. Withdraw Money")
        print("5. Transaction History")
        print("6. Logout")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            account_details(user["user_id"])

        elif choice == "2":
            account_details(user["user_id"])

        elif choice == "3":
            deposit(user["user_id"])

        elif choice == "4":
            withdraw(user["user_id"])

        elif choice == "5":
            transaction_history(user["user_id"])

        elif choice == "6":
            print("Logged out successfully.")
            break

        else:
            print("Invalid choice.")


# ==========================================
# ADMIN MENU
# ==========================================

def admin_menu():
    while True:
        print("\n================================")
        print("           ADMIN MENU")
        print("================================")
        print("1. View All Customers")
        print("2. View All Accounts")
        print("3. View All Transactions")
        print("4. Update Customer")
        print("5. Delete Customer")
        print("6. Logout")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            view_customers()

        elif choice == "2":
            view_accounts()

        elif choice == "3":
            view_all_transactions()

        elif choice == "4":
            update_customer()

        elif choice == "5":
            delete_customer()

        elif choice == "6":
            print("Logged out successfully.")
            break

        else:
            print("Invalid choice.")


# ==========================================
# MAIN PROGRAM
# ==========================================

def main():

    # Create database and tables automatically

    while True:

        print("\n======================================")
        print("     BANKING MANAGEMENT SYSTEM")
        print("======================================")
        print("1. Customer Registration")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            register()

        elif choice == "2":

            user = login()

            if user:

                if user["role"] == "admin":
                    admin_menu()

                elif user["role"] == "customer":
                    customer_menu(user)

        elif choice == "3":
            print("\nThank you for using Banking Management System.")
            break

        else:
            print("Invalid choice. Please try again.")


# ==========================================
# PROGRAM START
# ==========================================
main()