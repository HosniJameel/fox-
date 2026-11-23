// Renders scene1 (90 frames, opaque) and the overlay layer (240 frames, RGBA) to PNG sequences.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const b = await chromium.launch();
  for (const [page, n, dir, transparent] of [['scene1.html', 90, 'frames_s1', false], ['overlay.html', 240, 'frames_ov', true]]) {
    const out = path.join(__dirname, dir); fs.mkdirSync(out, { recursive: true });
    const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
    await p.goto('file://' + path.join(__dirname, page));
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
    for (let f = 0; f < n; f++) {
      await p.evaluate((f) => window.render(f), f);
      await p.screenshot({ path: path.join(out, String(f).padStart(3, '0') + '.png'), omitBackground: transparent });
    }
    await p.close(); console.log(dir, 'done');
  }
  await b.close();
})();
