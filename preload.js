const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  platform: process.platform,
  // Aquí podemos añadir funciones para interactuar con el sistema de archivos si fuera necesario
});
