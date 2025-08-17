# AI Research Paper Summarizer & Critic

## 📌 Project Overview
This project is an **AI-powered tool for analyzing research papers**.  
It allows users to upload a PDF research paper and receive:  
- 📑 **Summarization** of the paper’s key ideas.  
- 📝 **Critique/Review block** with strengths, weaknesses, methodology insights.  
- 📊 **Plagiarism & citation analysis** (basic implemented, advanced pending).  
- ⚡ Planned: **Fact-checking & visualization modules**.  

Built for academic use, this project aims to **reduce research overload** and help students, researchers, and reviewers quickly understand and critique scientific papers.

---

## ✅ Features Completed (till now)
### Backend
- [x] **PDF Text Extraction** (PyMuPDF → extract raw text).  
- [x] **Summarization Module** (HuggingFace Transformers – BART).  
- [x] **Critique Block** (auto-generated feedback on clarity, novelty, methodology, impact).  
- [x] **Basic Plagiarism Detection** (TF-IDF + cosine similarity stub – ready to extend).  
- [x] **Flask API** with /analyze endpoint for PDF uploads.  
- [x] **CORS Enabled** → backend ready for frontend integration.  

### Frontend
- [x] React project scaffolded (
px create-react-app frontend).  
- [x] Installed dependencies: **TailwindCSS, Axios, Recharts**.  
- [ ] UI for PDF upload & displaying results → **not coded yet**.  
- [ ] Integration with backend API → **pending**.  

---

## 🛠️ Tech Stack
- **Backend**: Python 3.12, Flask, Flask-CORS, PyMuPDF, HuggingFace Transformers, scikit-learn  
- **Frontend**: React.js, TailwindCSS, Axios, Recharts  
- **Other Tools**: Git, PowerShell, Virtualenv  

---

## ⚙️ Backend Setup

### 1️⃣ Create Virtual Environment
`powershell
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell
2️⃣ Install Dependencies

pip install -r requirements.txt
(We generated requirements.txt using pip freeze > requirements.txt.)

3️⃣ Run Backend

python backend/app.py
Runs Flask server at: http://127.0.0.1:5000

Endpoint available:

POST /analyze → accepts a PDF file, returns JSON with summary and critique.

4️⃣ Example Test (via PowerShell / curl)
powershell
Copy
Edit
curl -X POST http://127.0.0.1:5000/analyze -F "file=@sample.pdf"
Response JSON:

json
Copy
Edit
{
  "summary": "This paper explores...",
  "critique": "Strengths: ... Weaknesses: ..."
}
⚙️ Frontend Setup (So far)
1️⃣ Create React App

npx create-react-app frontend
cd frontend
2️⃣ Install Dependencies

npm install axios recharts
npm install -D tailwindcss postcss autoprefixer
3️⃣ Tailwind Init (troubleshooting needed in Windows PowerShell)

npx tailwindcss init -p
⚠️ Currently, Tailwind CLI is not detected in PowerShell.
(Workaround: use npx tailwindcss init -p in Git Bash / CMD, or manually create tailwind.config.js.)

4️⃣ Current Status
React project exists at /frontend.

No UI components yet.

Next step: build PDF Upload form + connect to backend API.

🚀 Usage Flow (Backend Only – Current)
Start backend server.

Upload sample.pdf via curl or Postman.

Get JSON response with summary + critique.

📌 Current Status
✅ Backend core working (PDF → Summary + Critique).

⚠️ Frontend scaffolded, but no UI yet.

❌ Not integrated (user still needs Postman/curl).

📌 Next Steps / Future Work
 Build React frontend UI:

File upload button (PDF).

Display summary + critique in styled cards.

Show plagiarism score & charts with Recharts.

 Debug TailwindCSS setup for styling.

 Add citation + fact-checking modules.

 Deploy backend (Render/Heroku) & frontend (Vercel/Netlify).

👨‍💻 Contributors
Jathin – Backend development, project setup.

(Future) Teammates for frontend integration & testing.

📝 Notes
The repo includes .gitignore for .venv and node_modules → so GitHub repo size stays small.

Use requirements.txt + npm install to reproduce environment.

