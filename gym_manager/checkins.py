from gym_manager.database import Session, CheckIn

def log_checkin(member_id):
    session = Session()
    
    checkin = CheckIn(member_id=member_id)
    session.add(checkin)
    session.commit()
    session.close()
    return True, "Check-in recorded!"

def get_checkins_by_member(member_id):
    session = Session()
    checkins = session.query(CheckIn).filter_by(member_id=member_id).all()
    session.close()
    return checkins