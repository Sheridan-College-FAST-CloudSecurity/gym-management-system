# create_admin.py

import getpass
from werkzeug.security import generate_password_hash
from gym_manager.database import get_db_session, Admin

def create_admin_user():
    """Command-line script to create a new admin user."""
    session = get_db_session()
    try:
        print("--- Create New Admin User ---")
        username = input("Enter username: ").strip()

        # Check if user already exists
        if session.query(Admin).filter_by(username=username).first():
            print(f"Error: User '{username}' already exists.")
            return

        password = getpass.getpass("Enter password: ")
        password_confirm = getpass.getpass("Confirm password: ")

        if password != password_confirm:
            print("Error: Passwords do not match.")
            return

        password_hash = generate_password_hash(password)

        new_admin = Admin(username=username, password_hash=password_hash)
        session.add(new_admin)
        session.commit()

        print(f"Admin user '{username}' created successfully!")

    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_admin_user()