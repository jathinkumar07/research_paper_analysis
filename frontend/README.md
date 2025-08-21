# AI Research Critic - Frontend

A modern, responsive React TypeScript frontend for the AI Research Critic application. This web interface provides an intuitive way to upload PDF documents and view comprehensive analysis results including plagiarism detection, citation validation, and fact-checking.

## 🚀 Quick Start (Absolute Beginners)

### 📋 Prerequisites

Before running the frontend, you need:

1. **Node.js 16 or higher** installed on your computer
   - Download from: https://nodejs.org/
   - Choose the "LTS" version
   - Verify: Open terminal and type `node --version`

2. **Backend server running** on port 5000
   - Follow the backend setup instructions in the main README
   - The backend must be running before starting the frontend

### 🔧 Installation Steps

1. **Navigate to the frontend folder**:
```bash
cd frontend
```

2. **Install all dependencies**:
```bash
npm install
```
*This downloads all required JavaScript packages (may take a few minutes)*

3. **Verify environment configuration**:
   - Check that `.env` file exists in the `frontend/` folder
   - It should contain:
```
REACT_APP_API_URL=http://localhost:5000
```

4. **Start the development server**:
```bash
npm start
```

✅ **Success Check**:
- Your web browser should automatically open to `http://localhost:3000`
- You should see the "AI Research Critic" homepage
- Terminal should show "Compiled successfully!"

## 🌐 Using the Application

### 📤 Uploading Documents

1. **Go to the Home page** (`http://localhost:3000`)
2. **Upload a PDF file** in one of two ways:
   - **Drag & Drop**: Drag a PDF file onto the upload area
   - **Click to Browse**: Click "browse to upload" and select a file

3. **File Requirements**:
   - ✅ Must be a PDF file (.pdf extension)
   - ✅ Must be 10MB or smaller
   - ❌ Other file types will be rejected

### 🔍 Analyzing Documents

1. **Click "Analyze Document"** after uploading
2. **Wait for analysis** - you'll see a spinning loader
3. **Automatic redirect** to results page when complete
4. **Analysis includes**:
   - AI-generated summary
   - Plagiarism percentage with risk level
   - Citation validation results
   - Fact-checking of claims

### 📊 Viewing Results

The results page shows:

- **Statistics Cards**: Word count, plagiarism score, citation count
- **AI Summary**: Intelligent document overview
- **Plagiarism Analysis**: Color-coded risk assessment
  - 🟢 Green (0-15%): Low Risk
  - 🟡 Yellow (15-30%): Medium Risk  
  - 🔴 Red (30%+): High Risk
- **Citation Analysis**: List of found citations with validation status
- **Fact Check Results**: Verification of factual claims
- **Download Option**: Export results as JSON file

## 🛠️ Development Commands

### Available Scripts

```bash
npm start          # Start development server (http://localhost:3000)
npm run build      # Create production build
npm test           # Run test suite
npm run eject      # Eject from Create React App (not recommended)
```

### 🔧 Development Server

When you run `npm start`:
- ✅ Opens browser automatically
- ✅ Hot reload on file changes
- ✅ Shows compilation errors in browser
- ✅ Runs on `http://localhost:3000`

### 🏗️ Production Build

When you run `npm run build`:
- ✅ Creates optimized bundle
- ✅ Minifies JavaScript and CSS
- ✅ Outputs to `build/` folder
- ✅ Ready for deployment

## 📁 Project Structure

```
frontend/
├── public/                     # Static files (don't edit)
│   ├── index.html             # Main HTML template
│   ├── favicon.ico            # Website icon
│   └── manifest.json          # PWA configuration
├── src/                       # Source code (edit these files)
│   ├── components/            # Reusable UI components
│   │   └── Navbar.tsx         # Navigation bar
│   ├── pages/                 # Main application pages
│   │   ├── Home.tsx           # Upload page with drag & drop
│   │   ├── Results.tsx        # Analysis results display
│   │   └── About.tsx          # App information page
│   ├── services/              # API communication
│   │   └── api.ts             # Axios HTTP client setup
│   ├── types/                 # TypeScript type definitions
│   │   └── index.ts           # Interface definitions
│   ├── App.tsx                # Main app component with routing
│   ├── index.tsx              # Application entry point
│   └── index.css              # Global styles with TailwindCSS
├── .env                       # Environment variables
├── package.json               # Dependencies and scripts
├── tailwind.config.js         # TailwindCSS configuration
├── postcss.config.js          # PostCSS configuration
└── tsconfig.json              # TypeScript configuration
```

## 🎨 Technology Stack

### Core Technologies
- **React 18**: Modern JavaScript library for building user interfaces
- **TypeScript**: JavaScript with type safety
- **TailwindCSS**: Utility-first CSS framework for styling
- **React Router**: Client-side routing for navigation

### Key Libraries
- **Axios**: HTTP client for API requests
- **React Hooks**: Modern React state management
- **PostCSS**: CSS processing tool
- **Autoprefixer**: Automatic CSS vendor prefixes

## 🔧 Configuration Details

### Environment Variables

Create a `.env` file in the `frontend/` folder with:

```bash
# Backend API URL - MUST match your backend server
REACT_APP_API_URL=http://localhost:5000

# Optional: Custom port for development server
# PORT=3001
```

**Important Notes**:
- ⚠️ Environment variables MUST start with `REACT_APP_` to be accessible
- ⚠️ Changes to `.env` require restarting the development server
- ⚠️ Use `http://localhost:5000` (not `127.0.0.1` or `https`)

### TailwindCSS Configuration

The `tailwind.config.js` file is pre-configured to:
- ✅ Scan all TypeScript/JavaScript files for classes
- ✅ Include responsive design utilities
- ✅ Use standard color palette

### TypeScript Configuration

The `tsconfig.json` is set up for:
- ✅ Strict type checking
- ✅ Modern ES6+ features
- ✅ React JSX support
- ✅ Absolute imports from `src/`

## 🐛 Troubleshooting

### Common Frontend Issues

#### 🔴 "npm install" Fails
**Symptoms**: Error messages during dependency installation
**Solutions**:
1. Clear npm cache: `npm cache clean --force`
2. Delete existing files: `rm -rf node_modules package-lock.json`
3. Reinstall: `npm install`
4. Try using npm instead of yarn: `npm install --legacy-peer-deps`

#### 🔴 "Cannot Connect to Backend"
**Symptoms**: Network errors, API calls failing
**Solutions**:
1. ✅ Verify backend is running: Open `http://localhost:5000/health` in browser
2. ✅ Check `.env` file exists with correct URL
3. ✅ Restart frontend server: Stop with Ctrl+C, then `npm start`
4. ✅ Check for CORS issues in browser console

#### 🔴 Styling Not Working
**Symptoms**: Plain HTML appearance, no colors/layout
**Solutions**:
1. ✅ Verify TailwindCSS installation: `npm list tailwindcss`
2. ✅ Check `index.css` has TailwindCSS imports
3. ✅ Restart development server: `npm start`
4. ✅ Clear browser cache: Ctrl+F5 or Cmd+Shift+R

#### 🔴 TypeScript Errors
**Symptoms**: Red squiggly lines, compilation errors
**Solutions**:
1. ✅ Check file imports are correct
2. ✅ Verify all required props are passed to components
3. ✅ Run `npm run build` to see all errors at once

#### 🔴 Page Not Found (404)
**Symptoms**: Blank page or "Cannot GET /results"
**Solutions**:
1. ✅ Ensure you're using `http://localhost:3000` (not 3001 or other ports)
2. ✅ Check React Router is properly configured in `App.tsx`
3. ✅ Navigate using the navbar links, not direct URL typing

### 🔍 Debugging Tips

1. **Check Browser Console**:
   - Open browser Developer Tools (F12)
   - Look for red error messages in Console tab
   - Network tab shows API request failures

2. **Check Terminal Output**:
   - Frontend terminal shows compilation errors
   - Look for "Failed to compile" messages

3. **Verify File Structure**:
   - Ensure all files exist in correct locations
   - Check that imports match actual file paths

## 🌍 Network Configuration

### Accessing from Other Devices

To access the frontend from other devices on your network:

1. **Start with network access**:
```bash
npm start -- --host 0.0.0.0
```

2. **Find your computer's IP address**:
```bash
# On Windows:
ipconfig

# On macOS/Linux:
ifconfig | grep inet
```

3. **Update backend URL** in `.env`:
```bash
REACT_APP_API_URL=http://YOUR_IP_ADDRESS:5000
```

4. **Access from other devices**: `http://YOUR_IP_ADDRESS:3000`

## 📱 Mobile Responsiveness

The frontend is designed to work on all devices:
- 📱 **Mobile phones**: Touch-friendly drag & drop
- 📱 **Tablets**: Optimized layout and spacing
- 💻 **Desktop**: Full feature experience
- 🖥️ **Large screens**: Expanded grid layouts

## 🔒 Security Notes

- ✅ File validation prevents non-PDF uploads
- ✅ Size limits prevent large file attacks
- ✅ Environment variables keep API URLs configurable
- ✅ No sensitive data stored in frontend code

## 📈 Performance

- ✅ **Fast loading**: Optimized React build
- ✅ **Efficient bundling**: Code splitting and tree shaking
- ✅ **Responsive images**: Properly sized assets
- ✅ **Minimal dependencies**: Only essential packages

---

## 🆘 Still Having Issues?

### Step-by-Step Verification

1. ✅ **Check Node.js**: `node --version` (should be 16+)
2. ✅ **Check npm**: `npm --version`
3. ✅ **Check backend**: Open `http://localhost:5000/health`
4. ✅ **Check frontend folder**: `ls -la` should show all files
5. ✅ **Check .env file**: `cat .env` should show API URL
6. ✅ **Fresh install**: Delete `node_modules`, run `npm install`

### Getting More Help

If you're still stuck after trying all troubleshooting steps:
1. 📋 Copy the exact error message from your terminal
2. 🔍 Note which step you're stuck on
3. 💻 Include your operating system (Windows/Mac/Linux)
4. 📝 List what you've already tried

**Remember**: Both the backend (port 5000) AND frontend (port 3000) need to be running simultaneously for the application to work properly!

---

**🎯 Quick Success Check**: If you can see the homepage, upload a PDF, and get analysis results, everything is working perfectly! 🎉
