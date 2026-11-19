from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Scan, SiteList
from ..schemas import UserCreate, UserUpdate
from ..security import get_current_user, hash_password

router = APIRouter(prefix="/api/admin", tags=["admin"])

def admin_only(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Administrator access required")
    return user

# ---- User management ----
@router.get("/users")
def list_users(db: Session = Depends(get_db), admin=Depends(admin_only)):
    return [{"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role,
             "is_active": u.is_active, "created_at": u.created_at}
            for u in db.query(User).order_by(User.created_at.desc()).all()]

@router.post("/users")
def create_user(data: UserCreate, db: Session = Depends(get_db), admin=Depends(admin_only)):
    if db.query(User).filter(User.email == data.email.lower()).first():
        raise HTTPException(409, "Email already registered")
    u = User(email=data.email.lower(), full_name=data.full_name,
             password_hash=hash_password(data.password), role=data.role)
    db.add(u); db.commit(); db.refresh(u)
    return {"id": u.id, "email": u.email, "role": u.role, "is_active": u.is_active}

@router.put("/users/{user_id}")
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db),
                admin=Depends(admin_only)):
    u = db.query(User).get(user_id)
    if not u: raise HTTPException(404, "User not found")
    if u.role == "admin" and data.role and data.role != "admin":
        raise HTTPException(400, "Cannot change an administrator's role")
    if data.full_name is not None: u.full_name = data.full_name
    if data.role is not None: u.role = data.role
    if data.is_active is not None: u.is_active = data.is_active
    if data.password: u.password_hash = hash_password(data.password)
    db.commit()
    return {"id": u.id, "role": u.role, "is_active": u.is_active}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin=Depends(admin_only)):
    u = db.query(User).get(user_id)
    if not u: raise HTTPException(404, "User not found")
    if u.role == "admin": raise HTTPException(400, "Administrator accounts cannot be deleted")
    db.delete(u); db.commit()
    return {"deleted": user_id}

# ---- Site lists ----
@router.get("/sites")
def sites(db: Session = Depends(get_db), admin=Depends(admin_only)):
    return [{"id": s.id, "domain": s.domain, "list_type": s.list_type}
            for s in db.query(SiteList).all()]

@router.post("/sites")
def add_site(domain: str, list_type: str, db: Session = Depends(get_db),
             admin=Depends(admin_only)):
    if list_type not in ("trusted", "blocked"):
        raise HTTPException(400, "list_type must be trusted or blocked")
    s = SiteList(domain=domain.lower(), list_type=list_type, added_by=admin.id)
    db.add(s); db.commit(); db.refresh(s)
    return {"id": s.id, "domain": s.domain, "list_type": s.list_type}

@router.delete("/sites/{site_id}")
def del_site(site_id: int, db: Session = Depends(get_db), admin=Depends(admin_only)):
    s = db.query(SiteList).get(site_id)
    if not s: raise HTTPException(404, "Not found")
    db.delete(s); db.commit()
    return {"deleted": site_id}
