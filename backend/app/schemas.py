from pydantic import BaseModel 
from typing import Optional
from datetime import date

class StudentCreate(BaseModel):
    name: str
    contact: str
    seat_id: Optional[int]
    shift1: bool = False
    shift2: bool = False
    shift3: bool = False
    paid: bool = False
    date_of_joining: Optional[date] = None
    custom_fees: Optional[int] = None  # ✅ new field
    total_fee: Optional[int] = None
    status: Optional[str] = "active"



class StudentOut(StudentCreate):
    id: int
    seat_id: Optional[int] = None
    total_fee: Optional[int] = None
    custom_fees: Optional[int] = None

    class Config:
        orm_mode = True

class MonthlyPaymentBase(BaseModel):
    student_id: int
    month: str  # format: YYYY-MM
    amount: int
    paid: bool = False
    
    
class MonthlyPaymentCreate(MonthlyPaymentBase):
    pass

class MonthlyPaymentOut(MonthlyPaymentBase):
    id: int
    student: Optional[StudentOut]  # <- add this line

    class Config:
        orm_mode = True
    


class AdminLogin(BaseModel):
    username: str
    password: str

class AdminOut(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

