const { contextBridge, ipcRenderer } = require('electron');

// We expose a safe API object to the renderer process (Dashboard.html)
// under the global namespace 'forgeAPI'
contextBridge.exposeInMainWorld('forgeAPI', {
    // Only expose the specific IPC channels the frontend actually needs
    triggerUpdateImport: () => ipcRenderer.send('import-update')
});