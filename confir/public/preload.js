const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  logError: (msg) => ipcRenderer.send('renderer-error', msg)
});