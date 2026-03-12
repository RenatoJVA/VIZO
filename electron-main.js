const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let backendProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    title: "VIZO - MD Analysis Professional",
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'frontend/public/favicon.ico')
  });

  // Quitar la barra de menú predeterminada (File, Edit, etc.)
  mainWindow.setMenu(null);


  // En producción cargamos el archivo compilado de Vue
  const indexPath = path.join(__dirname, 'frontend/dist/index.html');
  console.log(`Cargando frontend desde: ${indexPath}`);
  
  mainWindow.loadFile(indexPath).catch(err => {
    console.error("Error al cargar el archivo index.html:", err);
  });

  // Abrir herramientas de desarrollo solo si sospechamos de errores
  // mainWindow.webContents.openDevTools();


  mainWindow.on('closed', () => {

    mainWindow = null;
  });
}

function startBackend() {
  const isDev = !app.isPackaged;
  
  let backendBinary = process.platform === 'win32' ? 'vizo-backend.exe' : 'vizo-backend';
  let backendPath;
  
  if (isDev) {
    backendPath = path.join(__dirname, 'backend', 'dist', backendBinary);
  } else {
    // En producción (empaquetado), electron-builder lo pone en Resources
    backendPath = path.join(process.resourcesPath, backendBinary);
  }

  console.log(`Iniciando backend en: ${backendPath}`);
  
  backendProcess = spawn(backendPath, [], {
    cwd: path.dirname(backendPath),
    stdio: 'pipe',
    windowsHide: true
  });


  backendProcess.stdout.on('data', (data) => console.log(`Backend: ${data}`));
  backendProcess.stderr.on('data', (data) => console.error(`Backend Error: ${data}`));

  backendProcess.on('error', (err) => {
    console.error('Error fatal al iniciar el backend:', err);
  });

  backendProcess.on('exit', (code, signal) => {
    if (code !== 0 && code !== null) {
      console.error(`BACKEND CRASHED: El proceso terminó con código ${code}. ¡Probablemente el puerto 8000 está ocupado!`);
    }
  });
}

app.on('ready', () => {
  startBackend();
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', () => {
  if (backendProcess) {
    console.log('Cerrando backend...');
    backendProcess.kill();
  }
});
