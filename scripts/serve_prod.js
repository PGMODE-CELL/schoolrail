const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 8080;
const API_PORT = process.env.API_PORT || 3001;
const ROOT = path.resolve(__dirname, '..');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.ttf': 'font/ttf',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
};

const APPS = {
  '/app': path.join(ROOT, 'app', 'dist'),
  '/parent': path.join(ROOT, 'parent-app', 'dist'),
  '/driver': path.join(ROOT, 'driver-app', 'dist'),
};

function proxyTo(host, port, pathname, req, res) {
  const opts = {
    hostname: host, port, path: pathname, method: req.method,
    headers: { ...req.headers, host: `${host}:${port}` },
  };
  const proxy = http.request(opts, (proxyRes) => {
    const headers = { ...proxyRes.headers };
    delete headers['transfer-encoding'];
    headers['access-control-allow-origin'] = '*';
    res.writeHead(proxyRes.statusCode, headers);
    proxyRes.pipe(res);
  });
  req.pipe(proxy);
  proxy.on('error', () => {
    res.writeHead(502, { 'Content-Type': 'text/plain' });
    res.end('Backend unavailable');
  });
}

http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');
  let pathname = url.pathname;

  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'access-control-allow-origin': '*',
      'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
      'access-control-allow-headers': 'Content-Type,Authorization',
    });
    res.end();
    return;
  }

  // Favicon
  if (pathname === '/favicon.ico') {
    res.writeHead(204); res.end();
    return;
  }

  // Root redirect
  if (pathname === '/') {
    res.writeHead(302, { 'Location': '/app/' });
    res.end();
    return;
  }

  // API proxy
  if (pathname.startsWith('/api')) {
    proxyTo('localhost', API_PORT, pathname + url.search, req, res);
    return;
  }

  // Serve PWA apps
  for (const [prefix, dir] of Object.entries(APPS)) {
    if (pathname === prefix || pathname.startsWith(prefix + '/')) {
      const relativePath = pathname.slice(prefix.length) || '/';
      const filePath = path.join(dir, relativePath === '/' ? 'index.html' : relativePath);
      fs.readFile(filePath, (err, data) => {
        if (err) {
          fs.readFile(path.join(dir, 'index.html'), (err2, data2) => {
            if (err2) { res.writeHead(404); res.end('Not found'); }
            else { res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' }); res.end(data2); }
          });
          return;
        }
        const ext = path.extname(filePath).toLowerCase();
        res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
        res.end(data);
      });
      return;
    }
  }

  // Serve Expo assets (_expo/, assets/) from any PWA dist
  if (pathname.startsWith('/_expo') || pathname.startsWith('/assets')) {
    const rel = pathname.startsWith('/') ? pathname.slice(1) : pathname;
    for (const [prefix, dir] of Object.entries(APPS)) {
      const filePath = path.join(dir, rel);
      if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
        const ext = path.extname(filePath).toLowerCase();
        res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
        fs.createReadStream(filePath).pipe(res);
        return;
      }
    }
    res.writeHead(404); res.end('Not found');
    return;
  }

  res.writeHead(404, { 'Content-Type': 'text/plain' });
  res.end('Not found');
}).listen(PORT, () => {
  console.log('');
  console.log('=== SchoolRail Production Server (port ' + PORT + ') ===');
  console.log('');
  console.log('  Parent App:  http://localhost:' + PORT + '/parent/');
  console.log('  Driver App:  http://localhost:' + PORT + '/driver/');
  console.log('  API:         http://localhost:' + PORT + '/api/v1/docs');
  console.log('');
});
