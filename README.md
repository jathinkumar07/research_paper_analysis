# AI Research Critic

A full-stack application for analyzing research papers with AI-powered tools including plagiarism detection, citation validation, content summarization, and research critique.

## Features

- 🔐 **Secure Authentication** - JWT-based auth with role-based access control
- 📄 **PDF Upload & Processing** - Extract text and metadata from research papers
- 🤖 **AI-Powered Analysis**:
  - Document summarization (HuggingFace BART + fallback)
  - Plagiarism detection via TF-IDF similarity
  - Citation validation using Semantic Scholar API
  - Research methodology critique
- 📊 **Interactive Dashboard** - View analysis results with charts and tables
- 📋 **PDF Report Generation** - Professional analysis reports with ReportLab
- 🎨 **Modern UI** - React with Tailwind CSS

## Tech Stack

### Backend
- **Python 3.10+** with Flask
- **SQLAlchemy** with SQLite (dev) / PostgreSQL (prod)
- **JWT Authentication** with Flask-JWT-Extended
- **PDF Processing** with PyMuPDF
- **AI/ML**: HuggingFace Transformers, scikit-learn
- **Report Generation**: ReportLab

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Recharts** for data visualization
- **Axios** for API communication

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Initialize the database**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

4. **Start the Flask server**
```bash
python app.py
```

Backend will run on `http://127.0.0.1:5000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start the React development server**
```bash
npm start
```

Frontend will run on `http://localhost:3000`

## Usage

1. **Register/Login** - Create an account or sign in
2. **Upload PDF** - Go to Upload page and select a research paper
3. **Run Analysis** - The system will automatically analyze the document
4. **View Results** - See summary, plagiarism score, citations, and critique
5. **Generate Report** - Download professional PDF reports
6. **Manage Reports** - View and download previous reports

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/refresh` - Refresh JWT token

### Documents
- `POST /documents/upload` - Upload PDF file
- `GET /documents/:id` - Get document details
- `GET /documents` - List user documents

### Analysis
- `POST /analysis/run` - Run analysis on document
- `GET /analysis/:id` - Get analysis results
- `GET /analysis` - List user analyses

### Reports
- `POST /reports/:analysis_id/generate` - Generate PDF report
- `GET /reports/:report_id/download` - Download report
- `GET /reports` - List user reports

## Configuration

### Backend Environment Variables (.env)
```
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
SQLALCHEMY_DATABASE_URI=sqlite:///instance/app.db
MAX_UPLOAD_MB=25
USE_HF_SUMMARIZER=true
```

### Frontend Environment Variables (.env)
```
REACT_APP_API_URL=http://127.0.0.1:5000
```

## Project Structure

```
ai-research-critic/
├── backend/
│   ├── src/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   └── utils/           # Utilities
│   ├── corpus/              # Reference documents for plagiarism
│   ├── uploads/             # Uploaded PDFs
│   ├── reports/             # Generated reports
│   └── app.py              # Flask application
└── frontend/
    ├── src/
    │   ├── components/      # Reusable UI components
    │   ├── pages/          # Application pages
    │   ├── contexts/       # React contexts
    │   └── api/            # API configuration
    └── public/             # Static assets
```

## Development Notes

- **Database**: SQLite for development, easily switchable to PostgreSQL
- **Authentication**: JWT tokens with automatic refresh
- **File Security**: UUIDs for stored filenames, size validation
- **Error Handling**: Centralized error handling with proper HTTP codes
- **Responsive Design**: Mobile-friendly UI with Tailwind CSS

## Production Deployment

1. **Backend**:
   - Set `FLASK_ENV=production`
   - Use PostgreSQL database
   - Configure proper CORS origins
   - Use production WSGI server (Gunicorn)

2. **Frontend**:
   - Build: `npm run build`
   - Serve static files with nginx/Apache
   - Update API URL for production backend

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## License

MIT License - see LICENSE file for details.

---

**Built with ❤️ using Flask, React, and AI-powered analysis tools.**

