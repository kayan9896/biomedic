const path = require('path');
const { app, BrowserWindow } = require('electron');
const { spawn, exec } = require('child_process');
const psTree = require('ps-tree'); // You'll need to install this package

let mainWindow;
let serverProcess;
let serverPID;

function killProcess(pid) {
  if (process.platform === 'win32') {
    // For Windows
    exec('taskkill /pid ' + pid + ' /T /F', (error, stdout, stderr) => {
      if (error) {
        console.error(`Error killing process: ${error}`);
      }
    });
  } else {
    // For Unix-based systems
    psTree(pid, (err, children) => {
      const pids = children.map(p => p.PID);
      pids.push(pid);
      pids.forEach(pid => {
        try {
          process.kill(pid, 'SIGKILL');
        } catch (e) {
          console.error(`Failed to kill process ${pid}: ${e}`);
        }
      });
    });
  }
}

function startServer() {
  const serverPath = isDev 
    ? path.join(__dirname, '../../dist/server.exe')
    : path.join(process.resourcesPath, 'server.exe');

  serverProcess = spawn(serverPath);
  serverPID = serverProcess.pid;

  serverProcess.stdout.on('data', (data) => {
    console.log(`Server stdout: ${data}`);
  });

  serverProcess.stderr.on('data', (data) => {
    console.error(`Server stderr: ${data}`);
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
  if (serverProcess) {
    killProcess(serverPID);
  }
  
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Add before-quit event handler
app.on('before-quit', (event) => {
  if (serverProcess) {
    event.preventDefault();
    killProcess(serverPID);
    setTimeout(() => {
      app.quit();
    }, 500); // Give some time for the process to be killed
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