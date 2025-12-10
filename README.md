Simple Applicant Tracking System (ATS)
-------------------------------------

This repository contains a minimal Django backend and React frontend for:
- Uploading multiple resume PDF files at once.
- Supply a job description (plain text).
- Each resume is parsed for text and scored against keywords from the job description.
- The API returns parsed contact fields and a percentage match for each resume.
- Frontend allows upload + shows ranked results.

Folders:
- backend: Django REST API
- frontend: React app (Vite + React)

Run instructions (quick):
1) Backend
   cd backend
   python -m venv venv
   source venv/bin/activate      # Linux/macOS
   venv\Scripts\activate       # Windows PowerShell
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver 8000

2) Frontend
   cd frontend
   npm install
   npm run dev      # Vite dev server runs on 5173 by default

API Endpoint:
POST http://localhost:8000/api/upload/
FormData fields:
- job_description (string)
- files[] (one or multiple PDF files)

Response: JSON list of results with 'filename', 'score' (0-100), parsed contacts, matched keywords.

Notes:
- This is a prototype. PDF parsing uses PyPDF2 and simple keyword-matching heuristics.
- Avoid resumes with tables/graphics; plain text resumes work best.

