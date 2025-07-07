from gym_manager.database import get_db_session, Payment, Member
from sqlalchemy.orm import joinedload

def record_payment(member_id, amount, method="Cash"):
    """Record a new payment in the database"""
    session = get_db_session()
    try:
        payment = Payment(
            member_id=member_id,
            amount=amount,
            payment_method=method
        )
        session.add(payment)
        session.commit()
        return True, "Payment recorded successfully!"
    except Exception as e:
        session.rollback()
        return False, f"Error recording payment: {str(e)}"
    finally:
        session.close()

def get_payments_by_member(member_id):
    """Get all payments for a specific member"""
    session = get_db_session()
    try:
        return session.query(Payment).filter_by(member_id=member_id).all()
    finally:
        session.close()

def get_all_payments():
    """Get all payments with member information (eager loading)"""
    session = get_db_session()
    try:
        payments = session.query(Payment).options(
            joinedload(Payment.member)
        ).order_by(Payment.payment_date.desc()).all()
        
        # Force loading of relationships before session closes
        for payment in payments:
            _ = payment.member.first_name
            
        return payments
    finally:
        session.close()

def delete_payment(payment_id):
    """Delete a payment from the database"""
    session = get_db_session()
    try:
        payment = session.query(Payment).filter_by(id=payment_id).first()
        if payment:
            session.delete(payment)
            session.commit()
            return True, "Payment deleted successfully!"
        return False, "Payment not found"
    except Exception as e:
        session.rollback()
        return False, f"Error deleting payment: {str(e)}"
    finally:
        session.close()