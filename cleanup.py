# cleanup.py
from gym_manager.database import get_db_session, Payment, Member

def cleanup_orphan_payments():
    session = get_db_session()
    try:
        # Find all payments where the associated member does not exist
        orphan_payments = session.query(Payment).filter(~Payment.member.has()).all()

        if not orphan_payments:
            print("No orphan payments found. Database is clean.")
            return

        print(f"Found {len(orphan_payments)} orphan payment(s). Deleting them...")
        for payment in orphan_payments:
            print(f"  - Deleting payment ID: {payment.id} for non-existent member ID: {payment.member_id}")
            session.delete(payment)

        session.commit()
        print("Cleanup complete.")

    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    cleanup_orphan_payments()