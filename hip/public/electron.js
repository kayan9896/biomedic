const path = require('path');
const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
let isDev;
import('electron-is-dev').then(module => {
  isDev = module.default;
});

let mainWindow;
let serverProcess;

function startServer() {
  // Path to your server executable
  const serverPath = isDev 
    ? path.join(__dirname, '../../dist/server.exe')
    : path.join(process.resourcesPath, 'server.exe');

  serverProcess = spawn(serverPath);

  serverProcess.stdout.on('data', (data) => {
    console.log(`Server stdout: ${data}`);
  });

  serverProcess.stderr.on('data', (data) => {
    console.error(`Server stderr: ${data}`);
  });

  serverProcess.on('close', (code) => {
    console.log(`Server process exited with code ${code}`);
  });
}

function createWindow() {
  // Start the server first
  startServer();

  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true
    }
  });

  // Load the index.html from a url
  mainWindow.loadURL(
    isDev
      ? 'http://localhost:3000'
      : `file://${path.join(__dirname, '../build/index.html')}`
  );
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  // Kill the server process when closing the app
  if (serverProcess) {
    serverProcess.kill();
  }
  
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Handle app quit
app.on('quit', () => {
  if (serverProcess) {
    serverProcess.kill();
  }
});