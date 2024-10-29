from sqlalchemy import String, Column, Enum, ForeignKey, Float, Date, Integer, CHAR , Boolean
from sqlalchemy.sql import func
from connection import base
from sqlalchemy.orm import relationship

class companyRegistration(base):
    __tablename__ = "company"
    company_user = Column(String(50), primary_key=True)
    mail = Column(String(200), nullable=False, unique=True)
    password = Column(String(80), nullable=False)
    
    # Relación bidireccional hacia los workers
    tworker = relationship("workerRegistrastion", back_populates="tcompany")
    
    url_image = Column(String(100))
    
class workerRegistrastion(base):
    __tablename__ = "worker"
    wname = Column(String(50), nullable=False, unique=True)
    password = Column(String(80), nullable=False)
    document = Column(String(50), primary_key=True, nullable=False)
    company = Column(String(50), ForeignKey('company.company_user'), nullable=False)
    
    #Relacion birideccional hacia la company
    tcompany = relationship("companyRegistration", back_populates="tworker")
    tbill = relationship("billRegistrastion", back_populates="tworker")
    
    wrole = Column(Enum("Gerente","Administrador","Colaborador"), default="Gerente", nullable=False)
    

class billRegistrastion(base):  
    __tablename__ = "bill"
    bill_number = Column(String(20), primary_key=True, nullable=False)
    total_price = Column(Float(), nullable=False)
    entry_date = Column(Date(), default=func.current_date(), nullable=False)
    due = Column(Float(), nullable=False)
    client_name = Column(String(30), nullable=False)
    client_phone = Column(String(20), nullable=False)
    payment = Column(Float())
    wname = Column(String(50), ForeignKey('worker.wname') ,nullable=False)
    
    ##Relacion bidireccional 
    tworker = relationship("workerRegistrastion", back_populates="tbill")
    tphone = relationship("phoneRegistrastion", back_populates="tbill")
    

     
class phoneRegistrastion(base):
    __tablename__ = "phone"
    phone_ref = Column(String(20), primary_key=True, nullable=False)
    bill_number = Column(String(20),ForeignKey('bill.bill_number') ,nullable=False)
    brand_name = Column(String(60), ForeignKey('brands.name'),nullable=False)
    device = Column(String(50), nullable=False)
    details = Column(String(250), nullable=False)
    individual_price = Column(Integer, nullable=False)
    repaired = Column(Boolean(),default=False)
    delivered = Column(Boolean(),default=False)
    date_delivered = Column(Date())
    tbrand = relationship("BrandsRegistration", back_populates="tphone")
    tbill = relationship("billRegistrastion", back_populates="tphone")
    

class BrandsRegistration(base):
    __tablename__ = "brands"
    id = Column(Integer,unique=True , autoincrement=True) 
    name = Column(String(60),primary_key=True, index=True)        
    
    tphone = relationship("phoneRegistrastion", back_populates="tbrand")
    tdevice = relationship("devicesRegistration", back_populates="tbrand")

class devicesRegistration(base):
    __tablename__ = "devices"
    id_brands = Column(String(60), ForeignKey('brands.name'))
    name = Column(String(80), primary_key=True)
    
    tbrand = relationship("BrandsRegistration", back_populates="tdevice")