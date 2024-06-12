from pydantic import BaseModel

class Clients (BaseModel):
    name:str
    lastName:str
    dni:str
    rif:str
    email:str
    birthdate :str
    phone : str 
    
