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
    library_id: int  # ✅ NEW

class SeatOut(BaseModel):
    id: int
    seat_number: int

    class Config:
        orm_mode = True

class StudentOut(StudentCreate):
    id: int
    seat_id: Optional[int] = None
    total_fee: Optional[int] = None
    custom_fees: Optional[int] = None
    library_id: int  # ✅ Ensure it's present
    seat: Optional[SeatOut]

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

# class AdminOut(BaseModel):
#     id: int
#     username: str
#     role: str  # ✅ NEW
#     library_id: Optional[int]
#     status: str

#     class Config:
#         orm_mode = True


from datetime import date





class LibraryCreate(BaseModel):
    name: str
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    max_seats: int
    
    
class LibraryOut(LibraryCreate):
    id: int
    name: str

    class Config:
        orm_mode = True

class AdminCreate(BaseModel):
    username: str
    password: str
    library_id: Optional[int] = None

    class Config:
        orm_mode = True
        
        
class AdminOut(BaseModel):
    id: int
    username: str
    role: str
    library_id: Optional[int]
    status: str
    created_at: Optional[date]
    library: Optional[LibraryOut]

    class Config:
        orm_mode = True
        
        
class AdminChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    class Config:
        orm_mode = True
        
        
        
class MonthlyExpenseBase(BaseModel):
    name: str
    date: date
    amount: int
    description: Optional[str] = None
    category: Optional[str] = None
    
    

class MonthlyExpenseCreate(MonthlyExpenseBase):
    pass

class MonthlyExpenseOut(MonthlyExpenseBase):
    id: int
    month: str
    library_id: int
    created_at: Optional[date]

    class Config:
        orm_mode = True
