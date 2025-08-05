# check_db.py
from gym_manager.database import get_db_session, Admin

def check_admins():
    session = get_db_session()
    try:
        print("--- Checking Admins in Database ---")
        admins = session.query(Admin).all()
        if not admins:
            print("No admin users found in the database.")
            print("Please run 'python create_admin.py' to create one.")
            return

        for admin in admins:
            print(f"ID: {admin.id}, Username: '{admin.username}', Hash: {admin.password_hash[:30]}...")

        print("\n--- Check Complete ---")

    finally:
        session.close()

if __name__ == "__main__":
    check_admins()