const path = require('path');
const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
let isDev=false
const treeKill = require('tree-kill');

let mainWindow;
let serverProcess;

function startServer() {
  // Path to your server executable
  const serverPath = isDev 
    ? path.join(__dirname, '../../proto.exe')
    : path.join(process.resourcesPath, 'proto.exe');

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

function terminateServer() {
  return new Promise((resolve) => {
    if (serverProcess) {
      treeKill(serverProcess.pid, 'SIGTERM', (err) => {
        if (err) console.error('Failed to kill server process:', err);
        resolve(serverProcess.pid);
      });
      console.log()
    } else {
      resolve();
    }
  });
}

function createWindow() {
  // Start the server first
  startServer();

  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    fullscreen:true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    }
  });
  mainWindow.setMenuBarVisibility(false)
  // Load the index.html from a url
  mainWindow.loadURL(
    isDev
      ? 'http://localhost:3000'
      : `file://${path.join(__dirname, '../build/index.html')}`
  );
}

app.whenReady().then(createWindow);

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('window-all-closed', async () => {
  await terminateServer();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', async () => {
  await terminateServer();
});
