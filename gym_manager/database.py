from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# Define database engine and Session maker at module level
engine = create_engine('sqlite:///gym.db')
Session = sessionmaker(bind=engine)

class Member(Base):
    __tablename__ = 'members'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    join_date = Column(Date, default=datetime.now)
    membership_type = Column(String(50), default="Monthly")
    expiration_date = Column(Date)
    height = Column(Float)
    weight = Column(Float)
    emergency_contact = Column(String(100))
    
    payments = relationship("Payment", back_populates="member")

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    amount = Column(Float, nullable=False)
    payment_date = Column(Date, default=datetime.now)
    payment_method = Column(String(50), default="Cash")
    
    member = relationship("Member", back_populates="payments")

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(engine)

# Initialize tables when module is imported
init_db()

def get_db_session():
    """Return a new database session"""
    return Session()