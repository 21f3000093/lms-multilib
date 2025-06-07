from ..app.models import Admin
from ..app.database import SessionLocal
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

username = "admin"
password = "admin123"
hashed = pwd_context.hash(password)

admin = Admin(username=username, password=hashed)
db.add(admin)
db.commit()
print("✅ Admin created")
db.close()