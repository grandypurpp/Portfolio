// Renders smgp-motion-reel.html to an MP4: frames from headless Chromium, audio from the page's own synth.
// Usage: node render.js [out.mp4]   (needs playwright and ffmpeg)
//        node render.js --stills 2.9,7.5,12.5   (PNG stills only, for checking)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30, DUR = 36;
const page_url = 'file://' + path.join(__dirname, 'smgp-motion-reel.html') + '?render=1';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => { console.error('PAGE ERROR', e.message); process.exitCode = 1; });
  await page.goto(page_url);
  await page.evaluate(() => window.__ready);
  const grab = async t => Buffer.from((await page.evaluate(x => window.__frame(x), t)).split(',')[1], 'base64');

  const si = process.argv.indexOf('--stills');
  if (si > 0) {
    const dir = path.join(__dirname, 'stills'); fs.mkdirSync(dir, { recursive: true });
    for (const t of process.argv[si + 1].split(',').map(Number)) fs.writeFileSync(path.join(dir, `t${t.toFixed(2)}.png`), await grab(t));
    await browser.close(); return;
  }

  const out = process.argv[2] || path.join(__dirname, 'smgp-motion-reel.mp4');
  const wav = path.join(__dirname, 'audio.raw');
  fs.writeFileSync(wav, Buffer.from(await page.evaluate(() => window.__audio()), 'base64'));
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-f', 's16le', '-ar', '48000', '-ac', '2', '-i', wav,
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '7M', '-bufsize', '14M', '-pix_fmt', 'yuv420p', '-r', String(FPS),
    '-af', 'alimiter=limit=0.89', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise(r => ff.on('close', r));
  for (let f = 0; f < FPS * DUR; f++) {
    if (!ff.stdin.write(await grab(f / FPS))) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(`frame ${f}/${FPS * DUR}`);
  }
  ff.stdin.end(); const code = await done; fs.unlinkSync(wav);
  await browser.close(); console.log(code === 0 ? 'wrote ' + out : 'ffmpeg failed ' + code); process.exit(code);
})();
