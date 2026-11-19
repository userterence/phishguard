import re, math
from urllib.parse import urlparse
from collections import Counter
import tldextract

SUSPICIOUS_WORDS = ["login","verify","secure","account","update","confirm","signin",
                    "password","bank","pay","payment","billing","wallet","free","bonus",
                    "gift","urgent","alert","suspend","unlock"]

# Student-target phishing keyword groups -> category mapping
CATEGORY_KEYWORDS = {
    "academic":   ["grade","grades","exam","examination","result","transcript","professor",
                   "instructor","faculty","thesis","coursework","quiz","assessment"],
    "scholarship":["scholarship","grant","stipend","bursary","financial-aid","financialaid",
                   "fellowship","tuition-grant","allowance"],
    "account":    ["login","signin","sign-in","password","webmail","student-portal",
                   "lms","moodle","canvas","blackboard","sso","verify-account"],
    "enrollment": ["enroll","enrollment","enrolment","register","registration","subjects",
                   "subject-list","units","tuition","matriculation","add-drop"],
}

def _entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c/n) * math.log2(c/n) for c in counts.values())

def extract_features(url: str) -> dict:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    p = urlparse(url)
    host = p.hostname or ""
    ext = tldextract.extract(url)
    path = p.path or ""
    query = p.query or ""

    ip_regex = r"^(\d{1,3}\.){3}\d{1,3}$"
    return {
        "url_length": len(url),
        "host_length": len(host),
        "path_length": len(path),
        "num_dots": url.count("."),
        "num_hyphens": host.count("-"),
        "num_digits_host": sum(c.isdigit() for c in host),
        "num_special": sum(not c.isalnum() and c not in ".-/:" for c in url),
        "has_ip": int(bool(re.match(ip_regex, host))),
        "has_at": int("@" in url),
        "num_subdomains": max(len(ext.subdomain.split(".")) - 1, 0) if ext.subdomain else 0,
        "has_https": int(p.scheme == "https"),
        "is_shortener": int(ext.domain in {
            "bit","goo","tinyurl","t","ow","is","buff","rebrand","cutt","rb"
        }),
        "host_entropy": round(_entropy(host), 4),
        "suspicious_words": sum(w in url.lower() for w in SUSPICIOUS_WORDS),
        "punycode": int("xn--" in host),
        "port_present": int(p.port is not None),
    }

FEATURE_ORDER = list(extract_features("[example.com](http://example.com)").keys())

def vectorize(url: str):
    f = extract_features(url)
    return [f[k] for k in FEATURE_ORDER]

def detect_category(url: str) -> str:
    u = url.lower()
    best, score = "none", 0
    for cat, words in CATEGORY_KEYWORDS.items():
        s = sum(1 for w in words if w in u)
        if s > score:
            best, score = cat, s
    return best if score > 0 else "none"

def explain(f: dict, status: str) -> list:
    reasons = []
    if f["url_length"] > 75:      reasons.append("Unusually long URL")
    if f["has_ip"]:               reasons.append("IP address used instead of a domain name")
    if f["has_at"]:               reasons.append("'@' symbol can hide the real destination")
    if f["num_subdomains"] >= 3:  reasons.append("Excessive subdomains")
    if f["num_hyphens"] >= 3:     reasons.append("Many hyphens in the domain")
    if f["has_https"] == 0:       reasons.append("No HTTPS encryption")
    if f["suspicious_words"] >= 2:reasons.append("Contains multiple credential/urgency keywords")
    if f["punycode"]:             reasons.append("Punycode domain (possible homograph attack)")
    if f["is_shortener"]:         reasons.append("URL shortener hides true destination")
    if f["host_entropy"] > 3.5:   reasons.append("Random-looking domain name")
    if not reasons and status != "safe":
        reasons.append("Pattern matches typical phishing URL structure")
    return reasons
