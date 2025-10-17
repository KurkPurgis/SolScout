// index.js — SolScout / Railway / 8080

import express from 'express';

// Devis lubame .env; Railway-s pole vaja
if (process.env.NODE_ENV !== 'production') {
  try {
    const { default: dotenv } = await import('dotenv');
    dotenv.config();
  } catch (_) {
    // ignore if dotenv is not installed
  }
}

const app = express();
app.use(express.json({ type: ['application/json', 'text/plain'], limit: '2mb' }));

// ---- Keskkonnamuutujad (trim) ----
const TOKEN  = (process.env.TELEGRAM_TOKEN || '').trim();
const CHATID = (process.env.CHAT_ID || '').trim();
const HELIUS_AUTH = (process.env.HELIUS_AUTH || '').trim();

// ---- Telegrami saatmine (Node 18+: global fetch) ----
async function sendToTelegram(text) {
  if (!TOKEN || !CHATID) throw new Error('TELEGRAM_TOKEN või CHAT_ID puudub');
  const url = `https://api.telegram.org/bot${TOKEN}/sendMessage`;
  const body = { chat_id: CHATID, text, parse_mode: 'HTML', disable_web_page_preview: true };

  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const t = await r.text();
  if (!r.ok) throw new Error(`Telegram sendMessage ${r.status}: ${t}`);
  return t;
}

// ---- Heliuse sündmuse vormindus ----
function formatHeliusEvent(ev) {
  const wallet    = ev.feePayer || ev.fee_payer || '-';
  const txType    = ev.transaction_type || ev.type || 'UNKNOWN';
  const signature = ev.signature || '-';

  // Proovi leida esimene token-transfer (kui on)
  const tt     = Array.isArray(ev.tokenTransfers) && ev.tokenTransfers.length ? ev.tokenTransfers[0] : null;
  const mint   = tt?.mint || '-';
  const amount = tt?.tokenAmount ?? tt?.amount ?? '-';

  const tsMs    = Number(ev.timestamp || 0) * 1000;
  const whenUtc = tsMs ? new Date(tsMs).toISOString().replace('T', ' ').replace('Z', '') : '-';

  const title   = ev.description || 'Solana tehing';

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

// ---- Health & Diagnostics ----
app.get('/', (_req, res) => res.send('ok'));

// (valikuline) näita registreeritud radu
// app.get('/routes', (_req, res) => {
//   const routes = [];
//   app._router?.stack?.forEach((m) => {
//     if (m.route) {
//       const methods = Object.keys(m.route.methods).join(',').toUpperCase();
//       routes.push(`${methods} ${m.route.path}`);
//     }
//   });
//   res.json(routes);
// });

// ---- Telegram suitsutest ----
app.get('/test/telegram', async (_req, res) => {
  try {
    const payload = `✅ Test @ ${new Date().toISOString()}`;
    const resp = await sendToTelegram(payload);
    res.status(200).send(resp);
  } catch (e) {
    console.error('❌ /test/telegram error:', e);
    res.status(500).send(String(e));
  }
});

// ---- Helius webhook ----
app.post('/helius', async (req, res) => {
  try {
    // (valikuline) Authorization headeri kontroll
    if (HELIUS_AUTH) {
      const hdr = req.headers['authorization'];
      if (hdr !== HELIUS_AUTH) {
        console.warn('❌ Wrong Authorization header');
        return res.status(401).send('Unauthorized');
      }
    }

    // Logi lühidalt (ära prindi hiigelkehasid)
    console.log('🛰️ Headers:', JSON.stringify(req.headers, null, 2));
    console.log('🛰️ Body preview:', JSON.stringify(req.body)?.slice(0, 4000));

    // 👉 Vastame KOHE 200, et Helius ei timeoutiks ega retryks
    res.sendStatus(200);

    // Toeta nii [] kui ka { data: [] }
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
    // siia satub vaid enne 200 vastamist tekkinud viga
    console.error('❌ Webhook handler error:', e);
  }
});

// ---- Kuula 8080 peal (nagu kokku leppisime) ----
const HOST = '0.0.0.0';
const PORT = 8080;

app.listen(PORT, HOST, () => {
  console.log(`🚀 Listening on ${HOST}:${PORT}`);
});

// Graatsiline sulgemine (näed SIGTERM logis)
process.on('SIGTERM', () => {
  console.log('↘️  SIGTERM received, exiting...');
  process.exit(0);
});
