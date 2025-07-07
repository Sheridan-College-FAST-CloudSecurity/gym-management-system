from gym_manager.database import get_db_session, Member
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

def add_member(first_name, last_name, email, phone=None, membership_type="Monthly", height=None, weight=None, emergency_contact=None):
    """Add a new member to the database"""
    session = get_db_session()
    try:
        join_date = datetime.now().date()
        expiration_date = join_date + timedelta(days=365 if membership_type == "Annual" else 30)
        
        member = Member(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            join_date=join_date,
            membership_type=membership_type,
            expiration_date=expiration_date,
            height=height,
            weight=weight,
            emergency_contact=emergency_contact
        )
        
        session.add(member)
        session.commit()
        return True, "Member added successfully!"
    except SQLAlchemyError as e:
        session.rollback()
        return False, f"Database error: {str(e)}"
    except Exception as e:
        session.rollback()
        return False, f"Error adding member: {str(e)}"
    finally:
        session.close()

def get_all_members():
    """Get all members from the database"""
    session = get_db_session()
    try:
        return session.query(Member).order_by(Member.last_name, Member.first_name).all()
    except SQLAlchemyError as e:
        print(f"Database error getting members: {str(e)}")
        return []
    finally:
        session.close()

def get_member_by_id(member_id):
    """Get a single member by ID"""
    session = get_db_session()
    try:
        return session.query(Member).get(member_id)
    except SQLAlchemyError as e:
        print(f"Database error getting member: {str(e)}")
        return None
    finally:
        session.close()

def delete_member(member_id):
    """Delete a member from the database"""
    session = get_db_session()
    try:
        member = session.query(Member).get(member_id)
        if member:
            session.delete(member)
            session.commit()
            return True, "Member deleted successfully"
        return False, "Member not found"
    except SQLAlchemyError as e:
        session.rollback()
        return False, f"Database error deleting member: {str(e)}"
    except Exception as e:
        session.rollback()
        return False, f"Error deleting member: {str(e)}"
    finally:
        session.close()