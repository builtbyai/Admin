# SRLA Project Setup Guide for Windows

## Prerequisites Installation

### 1. Install Node.js and npm
1. Download Node.js from https://nodejs.org/
2. Choose the LTS version (recommended)
3. Run the installer and follow the prompts
4. Verify installation by opening a new Command Prompt or PowerShell and running:
   ```
   node --version
   npm --version
   ```

### 2. Install Python (for the backend)
1. Download Python from https://www.python.org/downloads/
2. Choose Python 3.8 or higher
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Verify installation:
   ```
   python --version
   pip --version
   ```

### 3. Install Git (if not already installed)
1. Download from https://git-scm.com/download/win
2. Run the installer with default settings
3. Verify:
   ```
   git --version
   ```

## Project Setup

### Backend Setup (Flask API)

1. Navigate to the backend directory:
   ```
   cd srla_webstack
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```
   # For Command Prompt:
   venv\Scripts\activate
   
   # For PowerShell:
   venv\Scripts\Activate.ps1
   ```

4. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a .env file:
   ```
   copy .env.example .env
   ```

6. Edit the .env file with your API keys (use Notepad or any text editor)

7. Initialize the database:
   ```
   python -c "from api.server import app, db; app.app_context().push(); db.create_all()"
   ```

8. Start the Flask server:
   ```
   python api/server.py
   ```
   The backend should now be running at http://localhost:8000

### Frontend Setup (Web Portal)

1. Open a new terminal/command prompt
2. The web frontend is static HTML/CSS/JS, so you can:
   - Open `srla_webstack/index.html` directly in a browser
   - Or use Python's built-in server:
     ```
     cd srla_webstack
     python -m http.server 3000
     ```
   - Then open http://localhost:3000 in your browser

### Mobile App Setup (React Native)

1. Open a new terminal/command prompt
2. Navigate to the mobile app directory:
   ```
   cd srla-mobile
   ```

3. Install Expo CLI globally:
   ```
   npm install -g expo-cli
   ```

4. Install project dependencies:
   ```
   npm install
   ```

5. Create a .env file:
   ```
   copy .env.example .env
   ```

6. Start the Expo development server:
   ```
   npm start
   ```
   or
   ```
   expo start
   ```

7. This will open Expo Dev Tools in your browser. From there you can:
   - Press `w` to open in web browser
   - Scan the QR code with Expo Go app on your phone
   - Press `a` for Android emulator (requires Android Studio)
   - Press `i` for iOS simulator (Mac only)

## Quick Start Commands

### Start Everything (3 terminals needed):

**Terminal 1 - Backend:**
```
cd srla_webstack
venv\Scripts\activate
python api/server.py
```

**Terminal 2 - Web Frontend:**
```
cd srla_webstack
python -m http.server 3000
```

**Terminal 3 - Mobile App:**
```
cd srla-mobile
npm start
```

## Troubleshooting

### npm not recognized
- Make sure Node.js is installed
- Close and reopen your terminal after installation
- Check if npm is in your PATH

### Python not recognized
- Ensure Python was added to PATH during installation
- Try using `py` instead of `python`

### Permission errors with PowerShell
Run this command as Administrator:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port already in use
- Change the port in the respective configuration
- Or find and stop the process using the port

### Mobile app not loading
- Ensure the backend is running
- Update API_BASE_URL in .env to your computer's IP address (not localhost) for physical device testing

## Next Steps

1. Access the web portal at http://localhost:3000
2. Create a test patient account
3. Test the appointment booking system
4. Try the AI chatbot
5. Test the mobile app on your device

## Support

If you encounter issues:
1. Check the console for error messages
2. Ensure all services are running
3. Verify your .env files are configured correctly
4. Check that all dependencies are installed
