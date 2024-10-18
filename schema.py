from enum import Enum
from pydantic import BaseModel as bm
from datetime import date

#Definicion del enum para wrole
class Wrole(str, Enum):
    admin = "Administrador"
    manager = "Gerente"
    collaborator = "Colaborador"

class status(bm):
    status:str

class statusrole(bm):
    status:str
    role:str


class company(bm):
    company_user:str
    mail:str
    password:str

class companylogin(bm):
    company_user:str
    password:str

class worker(bm):
    wname:str
    password:str
    document:str
    company:str
    wrole: Wrole

class workerlogin(bm):
    wname:str
    password:str
    
class collaborators(bm):
    wname:str
    document:str
    wrole:Wrole 

class brand(bm):
    name: str   
    
class device(bm):
    id_brands:str
    name:str
    
class phone(bm):
    brand_name:str
    device:str
    details:str
    price:int

class bill(bm):
    total_price:float
    due:float
    client_name:str
    client_phone:str
    payment:float
    wname:str
    phones: list[phone]
