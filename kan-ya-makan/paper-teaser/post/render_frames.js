// Renders the 240-frame composite. Writes timings.json (for the audio mix) and streams
// length-prefixed PNG frames to stdout. Background: bg/NNN.jpg (Kling plate, 30 fps) if present.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'compose.html'));
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
  const L = await p.evaluate(() => window.layout());
  fs.writeFileSync(path.join(__dirname, 'timings.json'), JSON.stringify({ words: L.W, strike: [76, 94], logo: [190, 222] }, null, 1));
  const useBg = fs.existsSync(path.join(__dirname, 'bg', '000.jpg'));
  for (let f = 0; f < 240; f++) {
    const src = useBg ? 'bg/' + String(f).padStart(3, '0') + '.jpg' : null;
    await p.evaluate(async ([f, src]) => {
      window.render(f, src);
      const img = document.getElementById('bg');
      if (!img.complete) await new Promise(r => img.onload = r);
      await img.decode();
    }, [f, src]);
    const buf = await p.screenshot({ type: 'png' });
    const h = Buffer.alloc(4); h.writeUInt32BE(buf.length);
    if (!process.stdout.write(Buffer.concat([h, buf]))) await new Promise(r => process.stdout.once('drain', r));
    if (f % 60 === 0) process.stderr.write('frame ' + f + '\n');
  }
  await b.close();
})();
