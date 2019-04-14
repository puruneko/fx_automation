'use strict';

// electron import
const electron = require('electron');
const remote = electron.remote;
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
const Menu = electron.Menu;
const {crashReporter, dialog} = require('electron');

// module import
const url = require('url');
const path = require('path');

crashReporter.start({
  productName: 'YourName',
  companyName: 'YourCompany',
  submitURL: 'https://your-domain.com/url-to-submit',
  autoSubmit: true
});

app.on('window-all-closed', function() {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('ready', function() {
  // メニューをアプリケーションに追加
  Menu.setApplicationMenu(menu);

  openWindow(process.cwd());
});

function openWindow (baseDir) {
  let win = new BrowserWindow({width: 800, height: 600, nodeIntegration: false});
  win.loadURL(url.format({
        pathname: path.resolve(__dirname, '../html/graph/graph.html'),
        protocol: 'file:',
        slashes: true
    }));
  // 開発ツールを有効化
  win.webContents.openDevTools();
  win.on('closed', function () {
    win = null;
  });
}

// メニュー情報の作成
const template = [
  {
    label: 'ReadUs',
    submenu: [
      {label: 'Quit',
        accelerator: 'Command+Q',
        click: function () {
          app.quit();
        }}
    ]
  }, {
    label: 'File',
    submenu: [
      {
        label: 'Open',
        accelerator: 'Command+O',
        click: function () {
          // 「ファイルを開く」ダイアログの呼び出し
          dialog.showOpenDialog({properties: ['openDirectory']}, function (baseDir) {
            if (baseDir && baseDir[0]) {
              openWindow(baseDir[0]);
            }
          })
        }
      }
    ]
  }, {
    label: 'View',
    submenu: [
      {label: 'Reload',
        accelerator: 'Command+R',
        click: function () {
          BrowserWindow.getFocusedWindow().reload();
        }},
      {
        label: 'Toggle DevTools',
        accelerator: 'Alt+Command+I',
        click: function () {
          BrowserWindow.getFocusedWindow().toggleDevTools();
        }
      }
    ]
  }
];

const menu = Menu.buildFromTemplate(template);