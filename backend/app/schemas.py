from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

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
    left_at: Optional[datetime] = None
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
    paid_at: Optional[datetime] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    next_due_date: Optional[date] = None

    class Config:
        orm_mode = True


class PublicReceiptOut(BaseModel):
    payment: MonthlyPaymentOut
    library_name: Optional[str] = None
    library_address: Optional[str] = None
    library_contact: Optional[str] = None


class StudentBulkPaymentCreate(BaseModel):
    start_month: str = Field(..., regex=r"^\d{4}-\d{2}$")
    number_of_months: int = Field(default=1, ge=1, le=24)
    mark_as_paid: bool = False
    total_amount_paid: Optional[int] = Field(default=None, ge=1)
    selected_months: Optional[List[str]] = None


class StudentBulkPaymentItem(BaseModel):
    payment_id: int
    month: str
    amount: int
    paid: bool
    action: str


class StudentBulkPaymentResult(BaseModel):
    created: int
    updated: int
    skipped: int
    payments: List[StudentBulkPaymentItem]
    


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


class NotificationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    category: str = Field(default="general", min_length=1, max_length=50)
    target_library_id: Optional[int] = None
    target_admin_ids: Optional[List[int]] = None
    click_url: Optional[str] = Field(default=None, max_length=500)


class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    category: str
    sender_admin_id: Optional[int]
    sender_username: Optional[str] = None
    target_type: str
    target_library_id: Optional[int]
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]
    recipient_count: int = 0
    unread_count: int = 0

    class Config:
        orm_mode = True


class NotificationInboxItem(BaseModel):
    recipient_id: int
    notification_id: int
    title: str
    message: str
    category: str
    created_at: datetime
    sender_username: Optional[str] = None
    target_library_id: Optional[int] = None
    is_read: bool
    read_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class NotificationUnreadCount(BaseModel):
    unread_count: int


class PushSubscriptionKeys(BaseModel):
    p256dh: str
    auth: str


class PushSubscriptionCreate(BaseModel):
    endpoint: str = Field(..., min_length=1)
    expirationTime: Optional[str] = None
    keys: PushSubscriptionKeys


class PushSubscriptionDelete(BaseModel):
    endpoint: str = Field(..., min_length=1)


class PushSubscriptionOut(BaseModel):
    id: int
    admin_id: int
    endpoint: str
    created_at: datetime
    updated_at: datetime
    last_seen_at: datetime

    class Config:
        orm_mode = True


class PushConfigOut(BaseModel):
    enabled: bool
    vapid_public_key: Optional[str] = None
