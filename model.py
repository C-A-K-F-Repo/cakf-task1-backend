import enum
from sqlalchemy import Column, String, Integer, Date, Enum, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class RoleEnum(enum.Enum):
    ADMINISTRATOR = "ADMINISTRATOR"
    ADVANCED_USER = "ADVANCED_USER"
    USER = "USER"


class UserModel(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    fullName = Column(String, nullable=False)
    dateOfBirth = Column(Date)
    deliveryAddress = Column(String)
    phoneNumber = Column(String)
    email = Column(String, unique=True, nullable=False)
    passwordHash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.USER)

    orders = relationship("OrderModel", back_populates="user")


class OrderModel(Base):
    __tablename__ = 'orders'

    id = Column(String, primary_key=True)
    userId = Column(String, ForeignKey('users.id'), nullable=False)

    orderDate = Column(Date)
    productTypeId = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)

    user = relationship("UserModel", back_populates="orders")