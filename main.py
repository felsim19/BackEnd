import bcrypt
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from connection import create, get_db
from model import base,companyRegistration, workerRegistrastion,billRegistrastion, phoneRegistrastion, BrandsRegistration, devicesRegistration
from schema import company, status, companylogin as cl, worker, workerlogin as wl,statusrole,collaborators as clb,bill, phone, brand , device, someBill as sb
from fastapi.middleware.cors import CORSMiddleware
import re
from sqlalchemy import desc, text 

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

base.metadata.create_all(bind=create)

# Sirve los archivos de la carpeta 'companyImg'
app.mount("/companyImg", StaticFiles(directory="companyImg"), name="companyImg")

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


@app.post("/loginWorker/{company_id}", response_model=statusrole)
async def loginworker(company_id:str,worker_user:wl, db:Session=Depends(get_db)):
    db_worker = db.query(workerRegistrastion).filter(workerRegistrastion.wname == worker_user.wname,
                                                     workerRegistrastion.company == company_id).first()
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

@app.get("/allcompany")
async def get_worker_count( db:Session=Depends(get_db)): 
    companis = db.query(companyRegistration).all()
    return companis

@app.get("/allcompany/{logeddcompany}")
async def get_worker_count(logeddcompany:str ,db:Session=Depends(get_db)): 
    companis = db.query(companyRegistration).filter(companyRegistration.company_user == logeddcompany).first()
    return companis


@app.get("/collaborators/{company_id}/workers")
async def get_collaborators( company_id:str, db:Session = Depends(get_db)):
    clb_list = db.query(workerRegistrastion).filter(workerRegistrastion.company == company_id).all()
    return clb_list
    
@app.get("/allBrands")
async def get_Brands(db: Session = Depends(get_db)):
    try:
        brands_list = db.query(BrandsRegistration).all()  # Consulta sin filtro
        if not brands_list:
            raise HTTPException(status_code=404, detail="No hay marcas registradas")
        return brands_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/allDevices")
async def get_Devices(db: Session = Depends(get_db)):
    try:
        Devices_list = db.query(devicesRegistration).all()  # Consulta sin filtro
        if not Devices_list:
            raise HTTPException(status_code=404, detail="No hay dispositvos registrados")
        return Devices_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/{id_brands}/Devices")
async def get_Devices(id_brands:str,db: Session = Depends(get_db)):
    try:
        Devices_list = db.query(devicesRegistration).filter(devicesRegistration.id_brands == id_brands).all()  # Consulta sin filtro
        if not Devices_list:
            raise HTTPException(status_code=404, detail="No hay dispositvos registrados")
        return Devices_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/Allbills")
async def getbills(db:Session=Depends(get_db)):
    try:
        bill_list = db.query(billRegistrastion).all()
        if not bill_list:
            raise HTTPException(status_code=404, detail="no hay facturas registradas")
        return bill_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/bill/{bill_number}")
async def getbill_number(bill_number:str,db:Session=Depends(get_db)):
    try:
        bill= db.query(billRegistrastion).filter(billRegistrastion.bill_number == bill_number).all()
        if not bill:
            raise HTTPException(status_code=404, detail="No hay facturas")
        return bill
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/billphone/{bill_number}")
async def getlistphone(bill_number:str, db:Session=Depends(get_db)):
    try:
        phone = db.query(phoneRegistrastion).filter(phoneRegistrastion.bill_number == bill_number).all()
        if not phone:
            raise HTTPException(status_code=404, detail="no hay dispositivos con esa factura")
        return phone
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/someDataOfBill", response_model=list[sb])
async def someDataBill(db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT bill_number, client_name, entry_date, total_price 
            FROM bill
        """)

        result = db.execute(query).mappings().all()  # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    
@app.delete("/deleteCollaborators/{company_id}/{wname}", response_model=status)
async def delete_collaborators(company_id:str,wname:str, db:Session = Depends(get_db)):
    # Buscar el trabajador por nombre y compañía
    worker = db.query(workerRegistrastion).filter(
        workerRegistrastion.company == company_id,
        workerRegistrastion.wname == wname
        ).first()
    
    if worker is None:
            raise HTTPException(status_code=404,detail="Trabajador no encontrado")
        
    db.delete(worker)
    db.commit()
    return status(status="Trabajador Eliminado Recientemente")


def generate_bill_number (db: Session):
    last_bill = db.query(billRegistrastion).order_by(desc(billRegistrastion.bill_number)).first()
    
    if last_bill:
        last_number = last_bill.bill_number[:-2]
        last_letter = last_bill.bill_number[-1]
        
        next_number = int(last_number) + 1
        
        if next_number > 9999:
            next_number = 1 
            last_letter = chr(ord(last_letter) + 1 )

        next_bill_number = f"{next_number:04d}-{last_letter}" 
        
    else:
        next_bill_number = "0001-A"
        
        
    return next_bill_number

def internal_reference (db: Session, bill_number:str):
    # Contar cuántos dispositivos ya están registrados con este número de factura
    devices_count = db.query(phoneRegistrastion).filter(phoneRegistrastion.bill_number == bill_number).count()
    
    # Incrementar el contador con base en el número de dispositivos ya registrados
    contador = devices_count + 1
    
    # Generar la referencia interna con el contador único
    references_int = f"{bill_number}-{contador}"    
       
    return references_int

@app.post("/newBrand", response_model=status)
async def createBrand(brand:brand, db:Session=Depends(get_db)):
    existing_brand = db.query(BrandsRegistration).filter(BrandsRegistration.name == brand.name).first()
    
    if existing_brand:
        raise HTTPException(status_code=403, detail="Esta marca ya esta registrada")
    
    new_brand = BrandsRegistration(
        name=brand.name
    )
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    
    return status(status="Marca registrada exitosamente")

@app.post("/newDevice", response_model=status)
async def createBrand(device:device, db:Session=Depends(get_db)):
    existing_device = db.query(devicesRegistration).filter(devicesRegistration.name == device.name).first()
    
    if existing_device:
        raise HTTPException(status_code=403, detail="Esta dispositivo ya esta registrado")
    
    new_device = devicesRegistration(
        id_brands=device.id_brands,
        name=device.name
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    
    return status(status="Marca registrada exitosamente")
    
    
@app.post("/createBillwithPhones", response_model=status)
async def createBillwithPhones(bill: bill, db: Session = Depends(get_db)):
    if len(bill.phones) > 5:
        raise HTTPException(status_code=400, detail="No se puede registrar más de 5 dispositivos") 
    
    bill_number = generate_bill_number(db)
    newbill = billRegistrastion(
        bill_number=bill_number,
        total_price=bill.total_price,
        due=bill.due,
        client_name=bill.client_name,
        client_phone=bill.client_phone,
        payment=bill.payment,
        wname=bill.wname
    )
    db.add(newbill)
    db.commit()
    db.refresh(newbill)
    
    for phone in bill.phones:
        new_phone = phoneRegistrastion(
            phone_ref=internal_reference(db, bill_number),
            bill_number=newbill.bill_number,
            brand_name=phone.brand_name,  # Cambiado a brand_name
            device=phone.device,
            details=phone.details,
            individual_price=phone.individual_price
        )
        db.add(new_phone)
        db.commit()
        db.refresh(new_phone)
        
    return status(status="Factura y dispositivos registrados exitosamente")      



@app.put("/putCompanyImage/{loggedCompany}", response_model=status)
async def putCompanyImage(loggedCompany:str, file: UploadFile = File(...) ,db:Session=Depends(get_db)):
    #Bucar la compañia
    try:
        company = db.query(companyRegistration).filter(companyRegistration.company_user == loggedCompany).first()
        image_content = await file.read()
        url_image = f"companyImg/{file.filename}"  # Ajusta la ruta según tu necesidad
        
        
        file_location = f"companyImg/{file.filename}"
        with open(file_location, "wb") as buffer:
            buffer.write(image_content)
        # Actualizar el campo url_img en la compañía
        company.url_image = url_image
        db.commit()  # Guardar los cambios
        db.refresh(company)  # Opcional: refrescar el objeto company con los nuevos datos

        return status(status="Image updated successfully")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    
