param(
  [string]$Port = "8080"
)

Write-Host "=== SchoolRail Production Server ===" -ForegroundColor Cyan
Write-Host ""

# Ensure backend is running
$pythonProc = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
if (-not $pythonProc) {
  Write-Host "Starting backend on port 3001..." -ForegroundColor Yellow
  $p = Start-Process python -ArgumentList "main.py" -WorkingDirectory "$PSScriptRoot\..\backend" -NoNewWindow -PassThru
  Start-Sleep -Seconds 3
  Write-Host "  Backend PID: $($p.Id)" -ForegroundColor Green
}

# Ensure admin dashboard is running
$nodeProc = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq "" }
if (-not (Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.Id -gt 0 })) {
  Write-Host "Starting admin dashboard on port 3000..." -ForegroundColor Yellow
  $p = Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -WorkingDirectory "$PSScriptRoot\..\admin" -PassThru
  Start-Sleep -Seconds 2
  Write-Host "  Admin PID: $($p.Id)" -ForegroundColor Green
}

# Build if dist doesn't exist
if (-not (Test-Path "$PSScriptRoot\..\parent-app\dist\index.html")) {
  Write-Host "Building parent PWA..." -ForegroundColor Yellow
  Set-Location "$PSScriptRoot\..\parent-app"
  npx expo export --platform web
}
if (-not (Test-Path "$PSScriptRoot\..\driver-app\dist\index.html")) {
  Write-Host "Building driver PWA..." -ForegroundColor Yellow
  Set-Location "$PSScriptRoot\..\driver-app"
  npx expo export --platform web
}

# Start production HTTP server
Write-Host ""
Write-Host "Starting production server on port $Port..." -ForegroundColor Yellow
Write-Host ""

$serverScript = @"
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = $Port;
const ROOT = path.resolve(__dirname, '..');

const MIME = {
  '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css',
  '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.ttf': 'font/ttf',
  '.woff': 'font/woff', '.woff2': 'font/woff2',
};

// Map URL paths to filesystem paths
const ROUTES = {
  '/parent':    path.join(ROOT, 'parent-app', 'dist'),
  '/driver':    path.join(ROOT, 'driver-app', 'dist'),
  '/admin':     'http://localhost:3000',
};

http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');
  let pathname = url.pathname;

  // Identify which app
  let appPath = ROUTES['/parent'];
  let serveDir = 'parent';
  if (pathname.startsWith('/driver')) { appPath = ROUTES['/driver']; serveDir = 'driver'; pathname = pathname.slice(7) || '/'; }
  else if (pathname.startsWith('/parent')) { pathname = pathname.slice(7) || '/'; }
  else if (pathname.startsWith('/admin') || pathname === '/') {
    // Proxy to admin
    const opts = { hostname: 'localhost', port: 3000, path: pathname === '/' ? '/admin' : pathname, method: req.method, headers: req.headers };
    const proxy = http.request(opts, (proxyRes) => { res.writeHead(proxyRes.statusCode, proxyRes.headers); proxyRes.pipe(res); });
    req.pipe(proxy);
    proxy.on('error', () => { res.writeHead(502); res.end('Admin dashboard down'); });
    return;
  }

  const filePath = path.join(appPath, pathname === '/' ? 'index.html' : pathname);

  // Serve PWA manifest and sw from correct path
  if (pathname === '/manifest.json') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      name: serveDir === 'driver' ? 'SchoolRail Driver' : 'SchoolRail Parent',
      short_name: 'SchoolRail',
      start_url: '/' + serveDir + '/',
      display: 'standalone',
      background_color: serveDir === 'driver' ? '#10B981' : '#6366F1',
      theme_color: serveDir === 'driver' ? '#10B981' : '#6366F1',
      icons: [
        { src: '/' + serveDir + '/icon-192.png', sizes: '192x192', type: 'image/png' },
        { src: '/' + serveDir + '/icon-512.png', sizes: '512x512', type: 'image/png' },
      ]
    }));
    return;
  }
  if (pathname === '/sw.js') {
    const swPath = path.join(appPath, 'sw.js');
    if (fs.existsSync(swPath)) {
      res.writeHead(200, { 'Content-Type': 'application/javascript' });
      res.end(fs.readFileSync(swPath));
    } else { res.writeHead(404); res.end(''); }
    return;
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      // SPA fallback: serve index.html
      fs.readFile(path.join(appPath, 'index.html'), (err2, data2) => {
        if (err2) { res.writeHead(404); res.end('Not found'); }
        else { res.writeHead(200, { 'Content-Type': 'text/html' }); res.end(data2); }
      });
      return;
    }
    const ext = path.extname(filePath);
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
    res.end(data);
  });
}).listen(PORT, () => {
  console.log('');
  console.log('=== SchoolRail Production URLs ===');
  console.log('  Admin:    http://localhost:' + PORT + '/admin');
  console.log('  Parent:   http://localhost:' + PORT + '/parent');
  console.log('  Driver:   http://localhost:' + PORT + '/driver');
  console.log('  Backend:  http://localhost:3001/docs');
  console.log('');
});
"@

# Write server script
$serverScript | Out-File -FilePath "$PSScriptRoot\serve_prod.js" -Encoding utf8

# Run the server
node "$PSScriptRoot\serve_prod.js"
