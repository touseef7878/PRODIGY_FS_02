#!/usr/bin/env node

/**
 * Employee Management System - Development Server
 * Automatically sets up and runs both backend and frontend servers
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m'
};

// Platform-specific configurations
const isWindows = os.platform() === 'win32';
const pythonCmd = 'python';
const activateCmd = isWindows ? 'venv\\Scripts\\activate.bat' : 'source venv/bin/activate';

class DevServer {
  constructor() {
    this.backendProcess = null;
    this.frontendProcess = null;
    this.setupComplete = false;
  }

  log(message, color = 'white', prefix = 'INFO') {
    const timestamp = new Date().toLocaleTimeString();
    console.log(`${colors[color]}[${timestamp}] [${prefix}] ${message}${colors.reset}`);
  }

  async checkPython() {
    return new Promise((resolve) => {
      exec('python --version', (error, stdout, stderr) => {
        if (error) {
          this.log('Python not found. Please install Python 3.8+ and ensure it\'s in your PATH.', 'red', 'ERROR');
          resolve(false);
        } else {
          this.log(`Found ${stdout.trim()}`, 'green', 'PYTHON');
          resolve(true);
        }
      });
    });
  }

  async setupEnvironment() {
    this.log('Setting up development environment...', 'cyan', 'SETUP');
    
    // Check if virtual environment exists
    const venvPath = path.join(__dirname, 'backend', 'venv');
    if (!fs.existsSync(venvPath)) {
      this.log('Creating Python virtual environment...', 'yellow', 'SETUP');
      await this.runCommand('python -m venv venv', path.join(__dirname, 'backend'));
    }

    // Install Python dependencies
    this.log('Installing Python dependencies...', 'yellow', 'SETUP');
    const pipInstall = isWindows 
      ? 'venv\\Scripts\\activate.bat && pip install -r requirements.txt'
      : 'source venv/bin/activate && pip install -r requirements.txt';
    
    await this.runCommand(pipInstall, path.join(__dirname, 'backend'));

    // Initialize database if it doesn't exist
    const dbPath = path.join(__dirname, 'backend', 'employee_management.db');
    if (!fs.existsSync(dbPath)) {
      this.log('Initializing database...', 'yellow', 'SETUP');
      const initDb = isWindows
        ? 'venv\\Scripts\\activate.bat && python ..\\scripts\\init_db.py'
        : 'source venv/bin/activate && python ../scripts/init_db.py';
      
      await this.runCommand(initDb, path.join(__dirname, 'backend'));
    }

    // Create .env if it doesn't exist
    const envPath = path.join(__dirname, '.env');
    const envExamplePath = path.join(__dirname, '.env.example');
    if (!fs.existsSync(envPath) && fs.existsSync(envExamplePath)) {
      fs.copyFileSync(envExamplePath, envPath);
      this.log('Created .env file from .env.example', 'green', 'SETUP');
    }

    this.setupComplete = true;
    this.log('Environment setup complete!', 'green', 'SETUP');
  }

  runCommand(command, cwd = __dirname) {
    return new Promise((resolve, reject) => {
      const shell = isWindows ? 'cmd.exe' : '/bin/bash';
      const shellFlag = isWindows ? '/c' : '-c';
      
      const child = spawn(shell, [shellFlag, command], {
        cwd,
        stdio: ['inherit', 'pipe', 'pipe']
      });

      let stdout = '';
      let stderr = '';

      child.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      child.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      child.on('close', (code) => {
        if (code === 0) {
          resolve(stdout);
        } else {
          reject(new Error(`Command failed with code ${code}: ${stderr}`));
        }
      });
    });
  }

  startBackend() {
    return new Promise((resolve, reject) => {
      this.log('Starting Flask backend server...', 'blue', 'BACKEND');
      
      const command = isWindows 
        ? 'venv\\Scripts\\activate.bat && python wsgi.py'
        : 'source venv/bin/activate && python wsgi.py';
      
      const shell = isWindows ? 'cmd.exe' : '/bin/bash';
      const shellFlag = isWindows ? '/c' : '-c';

      this.backendProcess = spawn(shell, [shellFlag, command], {
        cwd: path.join(__dirname, 'backend'),
        stdio: ['ignore', 'pipe', 'pipe']
      });

      this.backendProcess.stdout.on('data', (data) => {
        const output = data.toString().trim();
        if (output) {
          // Filter out some verbose output
          if (!output.includes('WARNING: This is a development server')) {
            this.log(output, 'blue', 'BACKEND');
          }
          
          // Check if server is ready (multiple possible indicators)
          if (output.includes('Running on') || 
              output.includes('Debug mode: on') || 
              output.includes('Debugger is active!')) {
            this.log('Backend server is ready on http://localhost:5000', 'green', 'BACKEND');
            resolve();
          }
        }
      });

      this.backendProcess.stderr.on('data', (data) => {
        const error = data.toString().trim();
        if (error && !error.includes('WARNING')) {
          this.log(error, 'red', 'BACKEND');
        }
      });

      this.backendProcess.on('close', (code) => {
        this.log(`Backend process exited with code ${code}`, 'yellow', 'BACKEND');
      });

      // Give backend time to start, then proceed
      setTimeout(() => {
        this.log('Backend server is starting...', 'green', 'BACKEND');
        resolve();
      }, 5000);
    });
  }

  startFrontend() {
    return new Promise((resolve) => {
      this.log('Starting frontend server...', 'green', 'FRONTEND');
      
      this.frontendProcess = spawn(pythonCmd, ['-m', 'http.server', '8000'], {
        cwd: path.join(__dirname, 'frontend'),
        stdio: ['ignore', 'pipe', 'pipe']
      });

      this.frontendProcess.stdout.on('data', (data) => {
        const output = data.toString().trim();
        if (output) {
          this.log(output, 'green', 'FRONTEND');
          if (output.includes('8000')) {
            this.log('Frontend server is ready on http://localhost:8000', 'green', 'FRONTEND');
            resolve();
          }
        }
      });

      this.frontendProcess.stderr.on('data', (data) => {
        const error = data.toString().trim();
        if (error) {
          this.log(error, 'red', 'FRONTEND');
        }
      });

      this.frontendProcess.on('close', (code) => {
        this.log(`Frontend process exited with code ${code}`, 'yellow', 'FRONTEND');
      });

      // Give frontend time to start
      setTimeout(() => {
        this.log('Frontend server is ready on http://localhost:8000', 'green', 'FRONTEND');
        resolve();
      }, 3000);
    });
  }

  async start() {
    console.log(`${colors.cyan}
╔══════════════════════════════════════════════════════════════╗
║           Employee Management System - Dev Server           ║
║                    HITEC University                         ║
╚══════════════════════════════════════════════════════════════╝
${colors.reset}`);

    try {
      // Check Python
      const pythonOk = await this.checkPython();
      if (!pythonOk) {
        process.exit(1);
      }

      // Setup environment
      await this.setupEnvironment();

      // Start servers
      this.log('Starting development servers...', 'cyan', 'DEV');
      
      // Start backend first, then frontend
      await this.startBackend();
      await this.startFrontend();
      
      // Show success message
      setTimeout(() => {
        console.log(`${colors.bright}${colors.green}
╔══════════════════════════════════════════════════════════════╗
║                    🎉 SERVERS ARE READY! 🎉                 ║
║                                                              ║
║  Frontend: http://localhost:8000                             ║
║  Backend:  http://localhost:5000                             ║
║  API Docs: http://localhost:5000/api/docs/                   ║
║                                                              ║
║  Login Credentials:                                          ║
║  Username: admin                                             ║
║  Password: ProdigyAdmin2024!                                 ║
║                                                              ║
║  Press Ctrl+C to stop all servers                           ║
╚══════════════════════════════════════════════════════════════╝
${colors.reset}`);
      }, 1000);

    } catch (error) {
      this.log(`Setup failed: ${error.message}`, 'red', 'ERROR');
      process.exit(1);
    }
  }

  stop() {
    this.log('Shutting down servers...', 'yellow', 'SHUTDOWN');
    
    if (this.backendProcess) {
      this.backendProcess.kill();
    }
    
    if (this.frontendProcess) {
      this.frontendProcess.kill();
    }
    
    this.log('All servers stopped. Goodbye!', 'green', 'SHUTDOWN');
    process.exit(0);
  }
}

// Handle graceful shutdown
const devServer = new DevServer();

process.on('SIGINT', () => {
  devServer.stop();
});

process.on('SIGTERM', () => {
  devServer.stop();
});

// Start the development server
devServer.start().catch((error) => {
  console.error('Failed to start development server:', error);
  process.exit(1);
});