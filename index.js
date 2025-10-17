import express from 'express';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(express.json({ type: ['application/json', 'text/plain'], limit: '2mb' }));

const TOKEN  = (process.env.TELEGRAM_TOKEN || '').trim();
const CHATID = (process.env.CHAT_ID || '').trim();

async function sendToTelegram(text) {
  if (!TOKEN || !CHATID) throw new Error('TELEGRAM_TOKEN või CHAT_ID puudub');
  const url = `https://api.telegram.org/bot${TOKEN}/sendMessage`;
  const body = { chat_id: CHATID, text, parse_mode: 'HTML', disable_web_page_preview: true };

  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type':'application/json' },
    body: JSON.stringify(body),
  });
  const t = await r.text();
  if (!r.ok) throw new Error(`Telegram sendMessage ${r.status}: ${t}`);
  return t;
}

function formatHeliusEvent(ev) {
  const wallet    = ev.feePayer || ev.fee_payer || '-';
  const txType    = ev.transaction_type || ev.type || 'UNKNOWN';
  const signature = ev.signature || '-';
  const tt        = Array.isArray(ev.tokenTransfers) && ev.tokenTransfers.length ? ev.tokenTransfers[0] : null;
  const mint      = tt?.mint || '-';
  const amount    = tt?.tokenAmount ?? tt?.amount ?? '-';
  const tsMs      = Number(ev.timestamp || 0) * 1000;
  const whenUtc   = tsMs ? new Date(tsMs).toISOString().replace('T',' ').replace('Z','') : '-';
  const title     = ev.description || 'Solana tehing';

  const lines = [
    '🟣 <b>' + title + '</b>',
    `Wallet: <code>${wallet}</code>`,
    `Tüüp: <b>${txType}</b>`,
    `Mint: <code>${mint}</code>`,
    `Kogus: <b>${amount}</b>`,
    `Aeg (UTC): ${whenUtc}`,
  ];
  if (signature && signature !== '-') lines.push(`Tx: https://solscan.io/tx/${signature}`);
  return lines.join('\n');
}

// Health-check
app.get('/', (_req, res) => res.send('ok'));

// Suitsetest Telegramile
app.get('/test/telegram', async (_req, res) => {
  try {
    const resp = await sendToTelegram(`✅ Test @ ${new Date().toISOString()}`);
    res.status(200).send(resp);
  } catch (e) {
    res.status(500).send(String(e));
  }
});

// Helius webhook
app.post('/helius', async (req, res) => {
  try {
    if (process.env.HELIUS_AUTH) {
      const hdr = req.headers['authorization'];
      if (hdr !== process.env.HELIUS_AUTH) {
        console.warn('❌ Wrong Authorization header');
        return res.status(401).send('Unauthorized');
      }
    }
    console.log('🛰️ Headers:', JSON.stringify(req.headers, null, 2));
    console.log('🛰️ Body preview:', JSON.stringify(req.body)?.slice(0, 4000));

    // Vastame KOHE 200, et Helius ei timeoutiks
    res.sendStatus(200);

    const raw = req.body;
    const events = Array.isArray(raw) ? raw : Array.isArray(raw?.data) ? raw.data : raw ? [raw] : [];
    if (!events.length) {
      console.warn('ℹ️ No events in payload');
      return;
    }

    for (const ev of events) {
      try {
        console.log('Processing signature:', ev?.signature || '-');
        const msg = formatHeliusEvent(ev);
        const tg = await sendToTelegram(msg);
        console.log('📨 Telegram OK:', tg);
      } catch (err) {
        console.error('❌ Telegram send failed:', err);
      }
    }
  } catch (e) {
    console.error('❌ Webhook handler error:', e);
  }
});


const PORT = Number(process.env.PORT) || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Listening on 0.0.0.0:${PORT}`);
});


process.on('SIGTERM', () => {
  console.log('↘️  SIGTERM received, exiting...');
  process.exit(0);
});
``
