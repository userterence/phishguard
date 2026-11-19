from fastapi import APIRouter

router = APIRouter(prefix="/api/awareness", tags=["awareness"])

MATERIALS = [
    {"id": 1, "title": "How to Spot a Fake Grade Portal",
     "category": "academic",
     "body": "Legitimate grade pages live on your official university domain. Check the "
             "address bar: a real portal will never use a hyphenated look-alike domain or a "
             "free web host. Grade notifications that push you to log in through a link are a "
             "classic credential-harvesting trick."},
    {"id": 2, "title": "Scholarship Offers That Ask You to Pay",
     "category": "scholarship",
     "body": "Real scholarships do not charge application or processing fees. Treat any "
             "grant requiring bank details, an OTP, or an upfront payment as fraud."},
    {"id": 3, "title": "Protecting Your Student Account",
     "category": "account",
     "body": "Enable two-factor authentication, never reuse your university password, and "
             "log in only from bookmarked official pages, not from emailed links."},
    {"id": 4, "title": "Enrollment and Tuition Payment Safety",
     "category": "enrollment",
     "body": "Verify the payment channel with the registrar before sending money. University "
             "payment pages sit on the official domain and always use HTTPS with a valid "
             "certificate for that domain."},
]

@router.get("/materials")
def materials():
    return MATERIALS
