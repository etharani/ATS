
# backend/ats_app/views.py
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound

from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

import re
import string
from PyPDF2 import PdfReader

# -----------------------
# HOME view (serve index)
# -----------------------
def home(request):
    """
    Serve the frontend index.html when visiting root (/).
    Looks for frontend/public/index.html relative to the project BASE_DIR.
    If not found, returns a small fallback page.
    """
    try:
        base = Path(settings.BASE_DIR)  # BASE_DIR is defined in settings.py
        # try public folder produced by Vite dev build or your frontend/public
        possible = [
            base / "frontend" / "public" / "index.html",
            base / "frontend" / "dist" / "index.html",   # built output
            base / "frontend_build" / "index.html",     # optional copy location
        ]
        for p in possible:
            if p.exists():
                html = p.read_text(encoding="utf-8")
                return HttpResponse(html)
    except Exception:
        # fall through to fallback
        pass

    # Fallback simple page (useful if index.html not found)
    fallback = """
    <!doctype html>
    <html>
      <head><meta charset="utf-8"><title>Simple ATS</title></head>
      <body>
        <h1>Simple ATS</h1>
        <p>Frontend not found at <code>frontend/public/index.html</code>.</p>
        <p>While developing, run the React dev server (Vite) and open <strong>http://localhost:5173</strong>.</p>
        <p>Or build the frontend and copy the <code>dist/</code> contents into <code>backend/frontend_build/</code> and try again.</p>
      </body>
    </html>
    """
    return HttpResponseNotFound(fallback)

# -----------------------
# Resume analysis helpers
# -----------------------
STOPWORDS = set([
    'the','and','for','with','that','this','from','are','was','will','have','has','but','not','you',
    'your','our','who','whom','what','which','when','where','how','all','any','may','can','a','an','in','on','to','of','by'
])

def extract_text_from_pdf(f):
    try:
        reader = PdfReader(f)
        text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        return "\n".join(text)
    except Exception:
        return ""

def tokenize(text):
    text = text.lower()
    # replace punctuation with spaces
    text = re.sub(r'['+re.escape(string.punctuation)+']', ' ', text)
    parts = re.split(r'\s+', text)
    tokens = [p for p in parts if p and len(p)>2 and p not in STOPWORDS]
    return tokens

def extract_contacts(text):
    emails = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text)
    phones = re.findall(r'(\+?\d[\d\-\s]{6,}\d)', text)
    linkedin = re.findall(r'linkedin\.com\/[A-Za-z0-9\-\_\/]+', text)
    github = re.findall(r'github\.com\/[A-Za-z0-9\-\_\/]+', text)
    # name heuristic: first non-empty line that has 2 words and at least one capitalized token
    name = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2 and any(w[0].isupper() for w in parts if w):
            # avoid lines that contain '@' or digits
            if '@' in line or any(ch.isdigit() for ch in line):
                continue
            name = line
            break
    return {
        'emails': list(dict.fromkeys(emails)),
        'phones': list(dict.fromkeys([p.strip() for p in phones])),
        'linkedin': list(dict.fromkeys(linkedin)),
        'github': list(dict.fromkeys(github)),
        'name': name
    }

def find_section_keywords(text, keywords):
    found = set()
    t = text.lower()
    for kw in keywords:
        if kw in t:
            found.add(kw)
    return sorted(list(found))

# -----------------------
# Upload API
# -----------------------
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_resumes(request):
    job_desc = request.data.get('job_description','')
    if not job_desc:
        return Response({'error':'Provide job_description field'}, status=400)
    # build keyword set
    tokens = tokenize(job_desc)
    keywords = sorted(list(dict.fromkeys(tokens)))
    if not keywords:
        return Response({'error':'No keywords parsed from job description'}, status=400)

    results = []
    files = request.FILES.getlist('files')
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile

    for f in files:
        # save to media/uploads/
        try:
            saved_name = default_storage.save(f"uploads/{f.name}", ContentFile(f.read()))
            download_url = request.build_absolute_uri(settings.MEDIA_URL + saved_name)
        except Exception:
            saved_name = None
            download_url = None

        # attempt to read content for analysis
        content = ""
        try:
            if saved_name:
                path = settings.MEDIA_ROOT / saved_name
                with open(path, 'rb') as fh:
                    content = extract_text_from_pdf(fh)
            else:
                # fallback: try reading from file-like object (may be consumed already)
                content = extract_text_from_pdf(f)
        except Exception:
            content = ""

        if not content:
            score = 0
            parsed = {'matches': [], 'contacts': {}}
        else:
            t = content.lower()
            matches = [k for k in keywords if k in t]
            # base score
            base = (len(matches)/len(keywords))*100
            # bonus for contact presence
            contacts = extract_contacts(content)
            bonus = 0
            if contacts['emails']:
                bonus += 5
            if contacts['phones']:
                bonus += 5
            if contacts['linkedin'] or contacts['github']:
                bonus += 3
            # bonus for 'skills','experience','education' mentions
            for sect in ['skill','experience','education','projects']:
                if sect in t:
                    bonus += 2
            score = min(100, round(base + bonus,2))
            parsed = {
                'matches': matches,
                'contacts': contacts
            }

        results.append({
            'filename': getattr(f,'name', 'unknown'),
            'score': score,
            'parsed': parsed,
            'download_url': download_url
        })

    # sort by score desc
    results = sorted(results, key=lambda x: x['score'], reverse=True)
    return Response({'keywords': keywords, 'results': results})
