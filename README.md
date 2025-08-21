# AI Research Critic

A complete full-stack application for analyzing research papers with AI-powered tools including plagiarism detection, citation validation, fact-checking, and document summarization.

## 🚀 Quick Start for Absolute Beginners

This guide will help you get the application running on your computer, even if you're new to programming.

### 📋 Prerequisites (What You Need to Install First)

Before starting, you need to install these tools on your computer:

1. **Python 3.10 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, **CHECK THE BOX** "Add Python to PATH"
   - Verify installation: Open terminal/command prompt and type `python --version`

2. **Node.js 16 or higher**
   - Download from: https://nodejs.org/
   - Choose the "LTS" (Long Term Support) version
   - This automatically installs `npm` (Node Package Manager)
   - Verify installation: Open terminal/command prompt and type `node --version`

3. **Git** (if not already installed)
   - Download from: https://git-scm.com/downloads
   - Verify installation: Type `git --version`

### 📥 Step 1: Download the Project

1. **Clone the repository** (download the code to your computer):
```bash
git clone <your-repository-url>
cd ai-research-critic
```

OR download as ZIP file and extract it, then navigate to the folder.

### 🐍 Step 2: Backend Setup (Python/Flask Server)

1. **Navigate to the backend folder**:
```bash
cd backend
```

2. **Create a virtual environment** (isolated Python environment):
```bash
# On Windows:
python -m venv venv
venv\Scripts\activate

# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Create environment file for backend**:
   - Create a file named `.env` in the `backend/` folder
   - Add this content to the file:
```
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-too
SQLALCHEMY_DATABASE_URI=sqlite:///instance/app.db
MAX_UPLOAD_MB=25
USE_HF_SUMMARIZER=true
```

5. **Start the backend server**:
```bash
python app.py
```

✅ **Success Check**: You should see:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

**Keep this terminal window open** - the backend server needs to stay running.

### ⚛️ Step 3: Frontend Setup (React Application)

**Open a NEW terminal window** (keep the backend running in the first one).

1. **Navigate to the frontend folder**:
```bash
cd frontend
```

2. **Install JavaScript dependencies**:
```bash
npm install
```

3. **Verify environment file**:
   - Check that `frontend/.env` exists with this content:
```
REACT_APP_API_URL=http://localhost:5000
```

4. **Start the frontend development server**:
```bash
npm start
```

✅ **Success Check**: 
- Your web browser should automatically open to `http://localhost:3000`
- You should see the "AI Research Critic" homepage
- The terminal should show "Compiled successfully!"

### 🎉 Step 4: Test the Application

1. **Open your web browser** to `http://localhost:3000`
2. **Upload a PDF file** by dragging and dropping or clicking "browse to upload"
3. **Click "Analyze Document"** - you should see a loading spinner
4. **View results** - the page should redirect to show analysis results

## 🛠️ Configuration Details

### Required Environment Variables

#### Backend Configuration (`backend/.env`)
| Variable | Description | Example Value | Required |
|----------|-------------|---------------|----------|
| `SECRET_KEY` | Flask secret key for sessions | `your-super-secret-key` | ✅ Yes |
| `JWT_SECRET_KEY` | JWT token encryption key | `your-jwt-secret-key` | ✅ Yes |
| `FLASK_ENV` | Flask environment mode | `development` | ✅ Yes |
| `SQLALCHEMY_DATABASE_URI` | Database connection string | `sqlite:///instance/app.db` | ✅ Yes |
| `MAX_UPLOAD_MB` | Maximum file upload size | `25` | ✅ Yes |
| `USE_HF_SUMMARIZER` | Use HuggingFace for summarization | `true` | ✅ Yes |

#### Frontend Configuration (`frontend/.env`)
| Variable | Description | Example Value | Required |
|----------|-------------|---------------|----------|
| `REACT_APP_API_URL` | Backend server URL | `http://localhost:5000` | ✅ Yes |

### 🔑 API Keys (Optional - For Enhanced Features)

The application works without API keys, but for enhanced functionality:

1. **Semantic Scholar API** (for citation validation):
   - No API key required - it's free
   - Automatically used by the backend

2. **HuggingFace API** (for better summarization):
   - Sign up at: https://huggingface.co/
   - Go to Settings → Access Tokens
   - Create a new token
   - Add to `backend/.env`: `HUGGINGFACE_API_TOKEN=your_token_here`

## 📱 Application Features

### 🏠 Home Page
- **Drag & Drop Upload**: Simply drag a PDF file onto the upload area
- **File Validation**: Automatically checks file type (PDF only) and size (≤10MB)
- **Progress Feedback**: Shows upload progress and analysis status

### 📊 Results Page
- **AI Summary**: Intelligent document summarization
- **Plagiarism Score**: Percentage with color-coded risk levels
- **Citation Analysis**: List of citations with validation status
- **Fact Checking**: Verification of factual claims
- **Download Results**: Export analysis as JSON file

### ℹ️ About Page
- **Feature Overview**: Detailed explanation of all capabilities
- **Technology Stack**: Complete list of technologies used
- **Usage Instructions**: Step-by-step guide

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Backend Issues

**Problem**: `ModuleNotFoundError` when starting backend
**Solution**: Make sure you activated the virtual environment and installed dependencies:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Problem**: `Port 5000 already in use`
**Solution**: 
- Kill the process using port 5000: `lsof -ti:5000 | xargs kill -9`
- Or change the port in `backend/app.py` and update `frontend/.env`

**Problem**: Database errors
**Solution**: Delete the database and recreate:
```bash
rm -rf backend/instance/
python app.py  # This will recreate the database
```

#### Frontend Issues

**Problem**: `npm install` fails
**Solution**: 
- Clear npm cache: `npm cache clean --force`
- Delete node_modules: `rm -rf node_modules package-lock.json`
- Reinstall: `npm install`

**Problem**: "Cannot connect to backend"
**Solution**: 
- Ensure backend is running on port 5000
- Check `frontend/.env` has correct URL: `REACT_APP_API_URL=http://localhost:5000`
- Restart frontend: `npm start`

**Problem**: Styling not working
**Solution**: 
- Ensure TailwindCSS is properly configured
- Restart the development server: `npm start`

### 🌐 Network Issues

**Problem**: Can't access from other devices
**Solution**: 
- Backend: Change `app.run(host='0.0.0.0')` in `backend/app.py`
- Frontend: Use `npm start -- --host 0.0.0.0`
- Update `REACT_APP_API_URL` to use your computer's IP address

## 📁 Project Structure

```
ai-research-critic/
├── backend/                    # Flask API server
│   ├── src/
│   │   ├── models/            # Database models
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   └── utils/             # Helper functions
│   ├── uploads/               # Uploaded PDF files
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Backend environment variables
├── frontend/                   # React web application
│   ├── public/                # Static files
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Application pages
│   │   ├── services/          # API communication
│   │   └── types/             # TypeScript definitions
│   ├── package.json           # JavaScript dependencies
│   └── .env                   # Frontend environment variables
└── README.md                  # This file
```

## 🔄 Development Workflow

### Making Changes

1. **Backend Changes**:
   - Edit files in `backend/src/`
   - Server auto-reloads in development mode
   - Test API endpoints at `http://localhost:5000`

2. **Frontend Changes**:
   - Edit files in `frontend/src/`
   - Browser auto-reloads when you save files
   - View changes at `http://localhost:3000`

### Testing

**Backend Testing**:
```bash
cd backend
python -m pytest tests/
```

**Frontend Testing**:
```bash
cd frontend
npm test
```

## 🚢 Production Deployment

### Backend Production
1. Set environment variables for production
2. Use PostgreSQL instead of SQLite
3. Use a production WSGI server like Gunicorn
4. Set up reverse proxy with nginx

### Frontend Production
1. Build the application:
```bash
cd frontend
npm run build
```
2. Serve the `build/` folder with a web server
3. Update `REACT_APP_API_URL` to point to production backend

## 🆘 Getting Help

### If You're Stuck

1. **Check the terminal output** - error messages usually tell you what's wrong
2. **Verify all prerequisites** are installed correctly
3. **Make sure both servers are running** (backend on port 5000, frontend on port 3000)
4. **Check environment files** exist and have correct values
5. **Try restarting both servers** - sometimes this fixes connection issues

### Common Beginner Mistakes

❌ **Forgetting to activate virtual environment** for Python
✅ **Always run** `source venv/bin/activate` before starting backend

❌ **Not keeping backend running** when testing frontend
✅ **Keep both terminals open** - one for backend, one for frontend

❌ **Wrong file paths** when creating .env files
✅ **Create .env files in the correct directories**: `backend/.env` and `frontend/.env`

❌ **Using wrong URLs** in environment files
✅ **Use exact URLs**: `http://localhost:5000` (not https, not 127.0.0.1)

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Make sure you followed each step exactly as written
4. Check that both servers are running without errors

---

**🎯 Success Indicators:**
- Backend terminal shows: "Running on http://127.0.0.1:5000"
- Frontend opens automatically in your browser at http://localhost:3000
- You can upload a PDF file and see analysis results

**Built with ❤️ using Flask, React, and AI-powered analysis tools.**

