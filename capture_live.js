const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');

async function capture(url, outPath, width = 1366, height = 768) {
  const chrome = spawn("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", [
    "--headless=new",
    "--disable-gpu",
    `--window-size=${width},${height}`,
    "--remote-debugging-port=9222",
    "about:blank"
  ]);

  await new Promise(r => setTimeout(r, 1200));

  const version = await new Promise((resolve, reject) => {
    http.get('http://127.0.0.1:9222/json/version', res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    }).on('error', reject);
  });

  const ws = new WebSocket(version.webSocketDebuggerUrl);
  await new Promise(r => ws.onopen = r);

  let id = 1;
  function send(method, params = {}) {
    return new Promise(resolve => {
      const msgId = id++;
      const handler = (event) => {
        const data = JSON.parse(event.data);
        if (data.id === msgId) {
          ws.removeEventListener('message', handler);
          resolve(data.result);
        }
      };
      ws.addEventListener('message', handler);
      ws.send(JSON.stringify({ id: msgId, method, params }));
    });
  }

  await send('Page.enable');
  await send('Page.navigate', { url });
  await new Promise(r => setTimeout(r, 2000));

  const screenshot = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(outPath, Buffer.from(screenshot.data, 'base64'));
  ws.close();
  chrome.kill();
  console.log('Saved ' + outPath);
}

async function main() {
  const scratch = "C:\\Users\\arham\\.gemini\\antigravity-ide\\brain\\5bebfa9e-3ef6-4fc8-9f74-206efdb9e015\\scratch";
  await capture("http://localhost:8000/?master=true&persona=einstein", `${scratch}\\live_einstein_1366.png`, 1366, 768);
  await capture("http://localhost:8000/?master=true&persona=kalam", `${scratch}\\live_kalam_1366.png`, 1366, 768);
  await capture("http://localhost:8000/?master=true&persona=tesla", `${scratch}\\live_tesla_1366.png`, 1366, 768);
}
main().catch(console.error);
