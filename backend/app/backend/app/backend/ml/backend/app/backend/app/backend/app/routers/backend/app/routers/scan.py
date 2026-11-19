from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from urllib.parse import urlparse
from ..database import get_db
from ..models import Scan, SiteList
from ..schemas import ScanIn, ScanOut
from ..security import get_current_user
from ..ml import classify

router = APIRouter(prefix="/api/scan", tags=["scan"])

def _domain(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return (urlparse(url).hostname or "").lower()

@router.post("", response_model=ScanOut)
def scan(data: ScanIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    domain = _domain(data.url)
    if not domain:
        raise HTTPException(400, "Invalid URL")

    # Admin-managed override lists take priority
    listed = db.query(SiteList).filter(SiteList.domain == domain).first()
    if listed and listed.list_type == "trusted":
        result = {"status": "safe", "category": "none", "confidence": None,
                  "reasons": ["Domain is on the administrator trusted list"]}
    elif listed and listed.list_type == "blocked":
        result = {"status": "phishing", "category": "account", "confidence": None,
                  "reasons": ["Domain is on the administrator blocked list"]}
    else:
        result = classify(data.url)

    row = Scan(user_id=user.id, url=data.url, domain=domain,
               status=result["status"], category=result["category"],
               confidence=result["confidence"], reasons=result["reasons"],
               source="extension")
    db.add(row); db.commit(); db.refresh(row)
    return row

@router.get("/history", response_model=list[ScanOut])
def history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return (db.query(Scan).filter(Scan.user_id == user.id)
              .order_by(Scan.created_at.desc()).limit(200).all())
