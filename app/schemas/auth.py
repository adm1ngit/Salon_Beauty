
from pydantic import BaseModel, EmailStr

class EmailLogin(BaseModel):
    email: EmailStr
    password: str
