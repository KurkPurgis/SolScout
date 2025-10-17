import express from 'express';
import fetch from 'node-fetch';
import dotenv from 'dotenv';
dotenv.config();

const app = express();
app.use(express.json({ limit: '1mb' }));

async function sendToTelegram(text) {
  const url = `https://api.telegram.org/bot${process.env.TELEGRAM_TOKEN}/sendMessage`;
  const body = { chat_id: process.env.CHAT_ID, text, parse_mode: 'HTML', disable_web_page_preview: true };
  const r = await fetch(url, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(`Telegram sendMessage failed ${r.status}: ${await r.text()}`);
}

app.post('/helius', async (req, res) => {
  try {
    if (process.env.HELIUS_AUTH) {
      const hdr = req.headers['authorization'];
      if (hdr !== process.env.HELIUS_AUTH) return res.status(401).send('Unauthorized');
    }
    const events = Array.isArray(req.body?.data) ? req.body.data : [];
    console.log('Webhook received:', JSON.stringify(req.body, null, 2));
    for (const ev of events) {
    console.log('Processing event:', JSON.stringify(ev, null, 2));
      const wallet    = ev.feePayer;
      const txType    = ev.type;                 // SWAP, TRANSFER, jne
      const signature = ev.signature;
      const tt        = (Array.isArray(ev.tokenTransfers) && ev.tokenTransfers[0]) || null;
      const mint      = tt?.mint || '-';
      const amount    = tt?.tokenAmount ?? '-';
      const tsMs      = Number(ev.timestamp || 0) * 1000;
      const whenUtc   = tsMs ? new Date(tsMs).toISOString().replace('T',' ').replace('Z','') : '-';

      const msg = [
        '🟣 <b>Solana tehing</b>',
        `Wallet: <code>${wallet}</code>`,
        `Tüüp: <b>${txType}</b>`,
        `Mint: <code>${mint}</code>`,
        `Kogus: <b>${amount}</b>`,
        `Aeg (UTC): ${whenUtc}`,
        `Tx: https://solscan.io/tx/${signature}`
      ].join('\n');

      await sendToTelegram(msg);
    }
    res.status(200).send('OK');      // vasta 200, muidu Helius retry'b
  } catch (e) {
    console.error(e);
    res.status(200).send('OK');
  }
});

app.get('/', (_, res) => res.send('OK'));
app.listen(process.env.PORT || 8080, () =>
  console.log(`Listening on :${process.env.PORT || 8080}`));
