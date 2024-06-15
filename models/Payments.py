from pydantic import BaseModel

class Pagos(BaseModel):
    IdContract : int 
    Amount : float
    Date : str
    PaymentType :str 