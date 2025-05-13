# NOT CORRECT
# from sqlalchemy import Column, Integer, String, Float
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

# class Device(Base):
#     __tablename__ = 'devices'

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True)
#     type = Column(String)
#     location = Column(String)

# class SensorData(Base):
#     __tablename__ = 'sensor_data'

#     id = Column(Integer, primary_key=True, index=True)
#     device_id = Column(Integer)
#     timestamp = Column(String)
#     value = Column(Float)

# class User(Base):
#     __tablename__ = 'users'

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
