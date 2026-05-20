#!/usr/bin/env python3
"""
Student Management System using MySQL
Requires: mysql-connector-python
Edit DB_CONFIG below with your MySQL credentials before running.
"""

import mysql.connector
from mysql.connector import errorcode
import sys

# <-- EDIT these with your MySQL details -->
DB_CONFIG = {
    "host": "localhost",
    "user": "your_mysql_user",
    "password": "your_mysql_password",
    "database": "studentdb",   # will be created if not exists
    "port": 3306
}
# ---------------------------------------

def get_server_conn():
    """Connect to server (no DB) for creating the database if needed."""
    cfg = DB_CONFIG.copy()
    cfg_no_db = {k: v for k, v in cfg.items() if k != "database"}
    return mysql.connector.connect(**cfg_no_db)

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    # create database if not exists, then create table
    try:
        srv = get_server_conn()
        srv.autocommit = True
        cur = srv.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` DEFAULT CHARACTER SET 'utf8mb4'")
        cur.close()
        srv.close()
    except mysql.connector.Error as err:
        print("❌ Could not create database:", err)
        sys.exit(1)

    # create table
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            roll VARCHAR(100) NOT NULL UNIQUE,
            age INT NULL,
            department VARCHAR(255) NULL,
            email VARCHAR(255) NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        conn.commit()
        cur.close()
        conn.close()
    except mysql.connector.Error as err:
        print("❌ Table creation failed:", err)
        sys.exit(1)

def add_student(name, roll, age=None, department=None, email=None):
    try:
        conn = get_conn()
        cur = conn.cursor()
        sql = "INSERT INTO students (name, roll, age, department, email) VALUES (%s, %s, %s, %s, %s)"
        cur.execute(sql, (name.strip(), roll.strip(), age, department, email))
        conn.commit()
        print(f"✅ Student '{name}' added with id {cur.lastrowid}.")
    except mysql.connector.IntegrityError as e:
        print("❌ Error: Roll must be unique or invalid data. ->", e)
    except mysql.connector.Error as e:
        print("❌ DB Error:", e)
    finally:
        cur.close()
        conn.close()

def list_students(limit=100):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, roll, age, department, email FROM students ORDER BY id LIMIT %s", (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        if not rows:
            print("No students found.")
            return
        print("-" * 72)
        print(f"{'ID':<4} {'Name':<20} {'Roll':<10} {'Age':<4} {'Department':<15} {'Email'}")
        print("-" * 72)
        for r in rows:
            print(f"{r[0]:<4} {r[1]:<20} {r[2]:<10} {str(r[3]) if r[3] else '':<4} {r[4] or '':<15} {r[5] or ''}")
        print("-" * 72)
    except mysql.connector.Error as e:
        print("❌ DB Error:", e)

def find_by_id(student_id):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, roll, age, department, email FROM students WHERE id = %s", (student_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except mysql.connector.Error as e:
        print(" DB Error:", e)
        return None

def search_students(keyword):
    kw = f"%{keyword}%"
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, roll, age, department, email
            FROM students
            WHERE name LIKE %s OR roll LIKE %s OR department LIKE %s OR email LIKE %s
            ORDER BY id
        """, (kw, kw, kw, kw))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except mysql.connector.Error as e:
        print(" DB Error:", e)
        return []

def update_student(student_id, **fields):
    allowed = ['name', 'roll', 'age', 'department', 'email']
    updates = []
    params = []
    for k, v in fields.items():
        if k in allowed and v is not None:
            updates.append(f"{k} = %s")
            params.append(v)
    if not updates:
        print("Nothing to update.")
        return
    params.append(student_id)
    sql = f"UPDATE students SET {', '.join(updates)} WHERE id = %s"
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, tuple(params))
        conn.commit()
        if cur.rowcount:
            print("✅ Student updated.")
        else:
            print(" No student found with that ID.")
    except mysql.connector.IntegrityError as e:
        print(" Update failed (possible duplicate roll). ->", e)
    except mysql.connector.Error as e:
        print(" DB Error:", e)
    finally:
        cur.close()
        conn.close()

def delete_student(student_id):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
        conn.commit()
        affected = cur.rowcount
        cur.close()
        conn.close()
        if affected:
            print("✅ Student deleted.")
        else:
            print("❌ No student found with that ID.")
    except mysql.connector.Error as e:
        print("❌ DB Error:", e)

def input_int(prompt, allow_empty=False):
    while True:
        s = input(prompt).strip()
        if s == "" and allow_empty:
            return None
        if s.isdigit():
            return int(s)
        print("Please enter a valid number or leave empty.")

def main_menu():
    while True:
        print("\n====== Student Management (MySQL) ======")
        print("1. Add student")
        print("2. List students")
        print("3. Search students")
        print("4. Update student")
        print("5. Delete student")
        print("6. Exit")
        choice = input("Choose (1-6): ").strip()
        if choice == "1":
            name = input("Name: ").strip()
            roll = input("Roll (unique): ").strip()
            age = input_int("Age (leave empty if unknown): ", allow_empty=True)
            dept = input("Department (leave empty if none): ").strip() or None
            email = input("Email (leave empty if none): ").strip() or None
            if not name or not roll:
                print("Name and Roll are required.")
            else:
                add_student(name, roll, age, dept, email)
        elif choice == "2":
            list_students()
        elif choice == "3":
            kw = input("Enter name/roll/department/email to search: ").strip()
            if not kw:
                print("Enter something to search.")
                continue
            rows = search_students(kw)
            if not rows:
                print("No results.")
            else:
                print("-" * 72)
                for r in rows:
                    print(f"ID:{r[0]} | Name:{r[1]} | Roll:{r[2]} | Age:{r[3] or ''} | Dept:{r[4] or ''} | Email:{r[5] or ''}")
                print("-" * 72)
        elif choice == "4":
            sid = input_int("Enter student ID to update: ")
            row = find_by_id(sid)
            if not row:
                print("No student with that ID.")
                continue
            print(f"Updating {row[1]} (press enter to keep current value)")
            name = input(f"Name [{row[1]}]: ").strip() or None
            roll = input(f"Roll [{row[2]}]: ").strip() or None
            age_input = input(f"Age [{row[3] or ''}]: ").strip()
            age = int(age_input) if age_input.isdigit() else None if age_input=="" else None
            dept = input(f"Department [{row[4] or ''}]: ").strip() or None
            email = input(f"Email [{row[5] or ''}]: ").strip() or None
            update_student(sid, name=name, roll=roll, age=age, department=dept, email=email)
        elif choice == "5":
            sid = input_int("Enter student ID to delete: ")
            confirm = input(f"Are you sure to delete id {sid}? (y/N): ").strip().lower()
            if confirm == 'y':
                delete_student(sid)
            else:
                print("Delete cancelled.")
        elif choice == "6":
            print("Bye!")
            sys.exit(0)
        else:
            print("Choose a valid option.")

if __name__ == "__main__":
    # validate DB credentials quickly
    try:
        # test connection
        test = get_server_conn()
        test.close()
    except mysql.connector.Error as e:
        print("❌ Can't connect to MySQL server. Check DB_CONFIG.", e)
        sys.exit(1)

    init_db()
    main_menu()
