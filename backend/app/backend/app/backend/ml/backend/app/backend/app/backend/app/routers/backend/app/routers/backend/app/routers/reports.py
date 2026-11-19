from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Report, Notification
from ..schemas import ReportIn, ReportReview
from ..security import get_current_user

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.post("")
def create_report(data: ReportIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    r = Report(user_id=user.id, url=data.url, category=data.category,
               description=data.description)
    db.add(r)
    db.add(Notification(user_id=user.id, title="Report submitted",
                        body=f"Your report for {data.url[:80]} is pending review."))
    db.commit(); db.refresh(r)
    return {"id": r.id, "status": r.status}

@router.get("/mine")
def my_reports(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = (db.query(Report).filter(Report.user_id == user.id)
              .order_by(Report.created_at.desc()).all())
    return [{"id": r.id, "url": r.url, "category": r.category, "status": r.status,
             "review_note": r.review_note, "created_at": r.created_at} for r in rows]

# Teachers + admins can view reports
@router.get("")
def all_reports(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("teacher", "admin"):
        raise HTTPException(403, "Insufficient permissions")
    rows = db.query(Report).order_by(Report.created_at.desc()).limit(300).all()
    return [{"id": r.id, "url": r.url, "category": r.category, "status": r.status,
             "description": r.description, "reporter": r.user.full_name if r.user else None,
             "created_at": r.created_at} for r in rows]

# Only admins can verify / reject / mark false-positive
@router.patch("/{report_id}")
def review(report_id: int, data: ReportReview, db: Session = Depends(get_db),
           user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Only administrators can review reports")
    r = db.query(Report).get(report_id)
    if not r:
        raise HTTPException(404, "Report not found")
    r.status, r.reviewer_id, r.review_note = data.status, user.id, data.review_note
    db.add(Notification(user_id=r.user_id, title="Report updated",
                        body=f"Your report for {r.url[:80]} was marked {data.status}."))
    db.commit()
    return {"id": r.id, "status": r.status}
