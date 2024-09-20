from enum import Enum
from pydantic import BaseModel as bm

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