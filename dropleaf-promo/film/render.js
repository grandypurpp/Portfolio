// node render.js reel|story [--stills 10,200,400]
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const V = process.argv[2] || '16x9', ROOT = __dirname, OUT = path.join(ROOT, 'out'); fs.mkdirSync(OUT, { recursive: true });
const types = { '.html': 'text/html', '.js': 'text/javascript', '.jpg': 'image/jpeg', '.png': 'image/png', '.woff2': 'font/woff2' };
const srv = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !fs.existsSync(p)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(r); });
srv.listen(0, async () => {
  const port = srv.address().port;
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: V === '9x16' ? { width: 1080, height: 1920 } : { width: 1920, height: 1080 } });
  page.on('pageerror', e => { console.error('PAGE ERROR', e.message); process.exitCode = 1; });
  page.on('console', m => m.type() === 'error' && console.error('console:', m.text()));
  await page.goto(`http://localhost:${port}/film.html?ar=${V}`);
  await page.evaluate(() => window.__ready);
  const N = await page.evaluate(() => window.__frames);
  const shot = async f => { await page.evaluate(x => window.renderFrame(x), f); return page.screenshot({ type: 'png' }); };
  const ri = process.argv.indexOf('--range');
  if (ri > 0) {
    const [ra, rb] = process.argv[ri + 1].split(',').map(Number);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', path.join(OUT, `${V}_seg.mp4`)], { stdio: ['pipe', 'inherit', 'inherit'] });
    const done = new Promise(r => ff.on('close', r));
    for (let f = ra; f < rb; f++) { if (!ff.stdin.write(await shot(f))) await new Promise(r => ff.stdin.once('drain', r)); }
    ff.stdin.end(); console.log('seg exit', await done); await browser.close(); srv.close(); return;
  }
  const si = process.argv.indexOf('--stills');
  if (si > 0) {
    for (const f of process.argv[si + 1].split(',').map(Number)) fs.writeFileSync(path.join(OUT, `${V}_f${String(f).padStart(4, '0')}.png`), await shot(f));
  } else {
    
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', '30', path.join(OUT, `${V}_video.mp4`)], { stdio: ['pipe', 'inherit', 'inherit'] });
    const done = new Promise(r => ff.on('close', r));
    for (let f = 0; f < N; f++) {
      if (!ff.stdin.write(await shot(f))) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 100 === 0) console.log(`${V} frame ${f}/${N}`);
    }
    ff.stdin.end(); console.log('ffmpeg exit', await done);
  }
  await browser.close(); srv.close();
});
