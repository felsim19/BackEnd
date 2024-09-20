from sqlalchemy import String, Column, Enum, ForeignKey
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
    
    wrole = Column(Enum("Gerente","Administrador","Colaborador"), default="Gerente", nullable=False)
    
    