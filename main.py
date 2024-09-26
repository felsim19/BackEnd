import bcrypt
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from connection import create, get_db
from model import base,companyRegistration, workerRegistrastion
from schema import company, status, companylogin as cl, worker, workerlogin as wl,statusrole,collaborators as clb
from fastapi.middleware.cors import CORSMiddleware
import re


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

base.metadata.create_all(bind=create)

regex_mail = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def is_valid_mail(mail:str) -> bool:
    return re.match(regex_mail,mail) is not None

@app.post("/insertCompany", response_model=status)
async def insertCompany(company:company, db:Session=Depends(get_db)):
    if not is_valid_mail(company.mail):
        raise HTTPException(status_code=401,detail="Correo no valido")
    name_company = db.query(companyRegistration).filter(companyRegistration.company_user==company.company_user).first()
    if name_company:
        raise HTTPException(status_code=401,detail="compañia ya existente")
    encriptacion = bcrypt.hashpw(company.password.encode("utf-8"), bcrypt.gensalt())
    data = companyRegistration(
        company_user=company.company_user,
        mail=company.mail,
        password=encriptacion.decode('utf-8')
    )
    db.add(data)
    db.commit()
    db.refresh(data)
    return status(status="La compañia a sido registrada correctamente")

@app.post("/loginCompany", response_model=status)
async def logincompany(company_user:cl, db:Session=Depends(get_db)):
    db_company = db.query(companyRegistration).filter(companyRegistration.company_user == company_user.company_user).first()
    if db_company is None:
        raise HTTPException(status_code=400, detail="Compañia no existe")
    if not bcrypt.checkpw(company_user.password.encode('utf-8'), db_company.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Contraseña Incorrecta")
    return status(status="Inicio de sesion exitoso")

@app.post("/insertWorker", response_model=status)
async def insertWorker(worker:worker, db:Session=Depends(get_db)):
    company = db.query(companyRegistration).filter(companyRegistration.company_user == worker.company).first()
    if not company:
        raise HTTPException(status_code=404, detail="Compañia no existe")
    
    # verificar si el primer trabajador de la compañia
    workers_count = db.query(workerRegistrastion).filter(workerRegistrastion.company == worker.company).count()
    assigned_role = worker.wrole
    if workers_count == 0 and assigned_role != "Gerente":
        raise HTTPException(status_code=401, detail="usted al ser el primer empleado tendra un rol de gerente")
    elif workers_count == 0 and assigned_role == "Gerente":
        assigned_role
    elif workers_count != 0 and assigned_role == "Gerente":
        raise HTTPException(status_code=401, detail="Solo puede haber un gerente por empresa")
    else:
        assigned_role 
        
    encryption = bcrypt.hashpw(worker.password.encode('utf-8'), bcrypt.gensalt())
    new_worker = workerRegistrastion(
        wname = worker.wname,
        password = encryption.decode('utf-8'),
        document = worker.document,
        company = worker.company,
        wrole = assigned_role
    )
    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)
    return status(status="Trabajador registrado exitosamente", msg="registro exitoso")


@app.post("/loginWorker", response_model=statusrole)
async def loginworker(worker_user:wl, db:Session=Depends(get_db)):
    db_worker = db.query(workerRegistrastion).filter(workerRegistrastion.wname == worker_user.wname).first()
    if db_worker is None:
        raise HTTPException(status_code=400, detail="nombre de usuario no existe")
    if not bcrypt.checkpw(worker_user.password.encode('utf-8'), db_worker.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Contraseña Incorrecta")
    return {
        "status": "Inicio de sesión exitoso",
        "role": db_worker.wrole
    }
    

@app.get("/company/{company_id}/workers/count")
async def get_worker_count(company_id:str, db:Session=Depends(get_db)): 
    count = db.query(workerRegistrastion).filter(workerRegistrastion.company == company_id).count()
    return {"count" : count }

@app.get("/collaborators/{company_id}/workers")
async def get_collaborators( company_id:str, db:Session = Depends(get_db)):
    clb_list = db.query(workerRegistrastion).filter(workerRegistrastion.company == company_id).all()
    return clb_list
    
    
