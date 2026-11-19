from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Scan, Report
from ..security import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

def _range(q, start, end, col):
    if start: q = q.filter(col >= start)
    if end:   q = q.filter(col <= end)
    return q

# ---- Admin dashboard ----
@router.get("/admin/overview")
def admin_overview(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role != "admin": return {"error": "forbidden"}
    total_students = db.query(User).filter(User.role == "student").count()
    total_teachers = db.query(User).filter(User.role == "teacher").count()
    total_scans = db.query(Scan).count()
    by_status = dict(db.query(Scan.status, func.count()).group_by(Scan.status).all())
    by_category = dict(db.query(Scan.category, func.count())
                         .filter(Scan.status != "safe").group_by(Scan.category).all())
    recent = (db.query(Scan).order_by(Scan.created_at.desc()).limit(10).all())
    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_scans": total_scans,
        "phishing": by_status.get("phishing", 0),
        "suspicious": by_status.get("suspicious", 0),
        "safe": by_status.get("safe", 0),
        "categories": by_category,
        "recent": [{"url": s.url, "status": s.status, "category": s.category,
                    "created_at": s.created_at} for s in recent],
    }

@router.get("/trends")
def trends(days: int = 14, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("admin", "teacher"): return {"error": "forbidden"}
    start = datetime.utcnow() - timedelta(days=days)
    rows = (db.query(func.date(Scan.created_at), Scan.status, func.count())
              .filter(Scan.created_at >= start)
              .group_by(func.date(Scan.created_at), Scan.status).all())
    out = {}
    for d, st, c in rows:
        out.setdefault(str(d), {"safe": 0, "suspicious": 0, "phishing": 0})[st] = c
    return out

# ---- Student dashboard ----
@router.get("/student/overview")
def student_overview(db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(Scan).filter(Scan.user_id == user.id)
    by_status = dict(q.with_entities(Scan.status, func.count()).group_by(Scan.status).all())
    recent = q.order_by(Scan.created_at.desc()).limit(10).all()
    return {"total_scans": q.count(),
            "phishing": by_status.get("phishing", 0),
            "suspicious": by_status.get("suspicious", 0),
            "safe": by_status.get("safe", 0),
            "reports": db.query(Report).filter(Report.user_id == user.id).count(),
            "recent": [{"url": s.url, "status": s.status, "category": s.category,
                        "created_at": s.created_at} for s in recent]}

# ---- Teacher dashboard ----
@router.get("/teacher/overview")
def teacher_overview(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("teacher", "admin"): return {"error": "forbidden"}
    by_status = dict(db.query(Scan.status, func.count()).group_by(Scan.status).all())
    by_category = dict(db.query(Scan.category, func.count())
                         .filter(Scan.status != "safe").group_by(Scan.category).all())
    return {"total_scans": db.query(Scan).count(),
            "phishing": by_status.get("phishing", 0),
            "suspicious": by_status.get("suspicious", 0),
            "safe": by_status.get("safe", 0),
            "categories": by_category,
            "pending_reports": db.query(Report).filter(Report.status == "pending").count()}
