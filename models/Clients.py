from pydantic import BaseModel

class Propietarios (BaseModel):
    name:str
    lastName:str
    dni:str
    rif:str
    email:str
    birthdate :str
    phone : str 
    address: str 
    CodePostal : str 
    
   
    
