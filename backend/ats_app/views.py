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
    Looks for frontend/public/index.html relative to the project BASE_DIR,
    then frontend/dist/index.html, then backend/frontend_build/index.html.
    If none found, returns a small fallback page.
    """
    try:
        base = Path(settings.BASE_DIR)
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
        pass

    # fallback page
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

# -----------------------------------
# Resume parsing / upload API view
# -----------------------------------

STOPWORDS = set([
    'the','and','for','with','that','this','from','are','was','will','have','has','but','not','you',
    'your','our','who','whom','what','which','when','where','how','all','any','may','can'
])

def extract_text_from_pdf(f):
    """
    Extract text from a PDF file-like object using PyPDF2.
    Returns combined text or empty string on failure.
    """
    try:
        # PdfReader accepts file-like object or path-like
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
    """
    Lowercase, remove punctuation, split into tokens,
    drop short/common stopwords.
    """
    text = text.lower()
    text = re.sub(r'[' + re.escape(string.punctuation) + ']', ' ', text)
    parts = re.split(r'\s+', text)
    tokens = [p for p in parts if p and len(p) > 2 and p not in STOPWORDS]
    return tokens

def extract_contacts(text):
    """
    Heuristic extraction of emails, phones, LinkedIn and GitHub, and a simple name guess.
    """
    emails = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text)
    phones = re.findall(r'(\+?\d[\d\-\s]{6,}\d)', text)
    linkedin = re.findall(r'linkedin\.com\/[A-Za-z0-9\-\_\/]+', text)
    github = re.findall(r'github\.com\/[A-Za-z0-9\-\_\/]+', text)

    name = None
    for line in text.splitlines():
        line = line.strip()
        if len(line.split()) >= 2 and sum(1 for w in line.split() if w[:1].isupper()) >= 1 and len(line) < 60:
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
    for kw in keywords:
        if kw in text:
            found.add(kw)
    return sorted(list(found))

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_resumes(request):
    """
    POST endpoint: expects multipart/form-data with:
      - job_description (string)
      - files (one or multiple PDF files)
    Returns JSON: { keywords: [...], results: [{filename, score, parsed}, ...] }
    """
    job_desc = request.data.get('job_description', '')
    if not job_desc:
        return Response({'error': 'Provide job_description field'}, status=400)

    # build keyword set from job description
    tokens = tokenize(job_desc)
    keywords = sorted(list(dict.fromkeys(tokens)))
    if not keywords:
        return Response({'error': 'No keywords parsed from job description'}, status=400)

    results = []
    files = request.FILES.getlist('files')
    for f in files:
        content = extract_text_from_pdf(f)
        if not content:
            score = 0
            parsed = {}
        else:
            t = content.lower()
            matches = [k for k in keywords if k in t]

            # base score: fraction of keywords found
            base = (len(matches) / len(keywords)) * 100 if keywords else 0

            # heuristic bonuses
            contacts = extract_contacts(content)
            bonus = 0
            if contacts['emails']:
                bonus += 5
            if contacts['phones']:
                bonus += 5
            if contacts['linkedin'] or contacts['github']:
                bonus += 3

            # small bonuses for presence of important sections/words
            for sect in ['skill', 'experience', 'education', 'projects']:
                if sect in t:
                    bonus += 2

            score = min(100, round(base + bonus, 2))

            parsed = {
                'matches': matches,
                'contacts': contacts
            }

        results.append({
            'filename': getattr(f, 'name', 'unknown'),
            'score': score,
            'parsed': parsed
        })

    # sort by score desc
    results = sorted(results, key=lambda x: x['score'], reverse=True)
    return Response({'keywords': keywords, 'results': results})

