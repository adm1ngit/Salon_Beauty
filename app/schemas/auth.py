
from pydantic import BaseModel

class PhoneLogin(BaseModel):
    phone: str
    password: str