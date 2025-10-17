// index.js — SolScout / Railway / 8080 + Axiom link

import express from 'express';

// .env ainult lokaalses arenduses; Railway-s ei ole vaja
if (process.env.NODE_ENV !== 'production') {
  try {
    const { default: dotenv } = await import('dotenv');
    dotenv.config();
  } catch (_) { /* ignore */ }
}

const app = express();
app.use(express.json({ type: ['application/json', 'text/plain'], limit: '2mb' }));

// ---- Env (trim) ----
const TOKEN          = (process.env.TELEGRAM_TOKEN || '').trim();
const CHATID         = (process.env.CHAT_ID || '').trim();
const HELIUS_AUTH    = (process.env.HELIUS_AUTH || '').trim();
// Axiom linki šabloon. Näide: https://cloud.axiom.co/.../search?q=signature:{signature}
const AXIOM_LINK_TPL = (process.env.AXIOM_LINK || '').trim();

const BUILD = 'solscout-axiom-2025-10-17';

// ---- Util: Axiom link {signature} asendusega ----
function buildAxiomLink(signature) {
  if (!AXIOM_LINK_TPL || !signature) return '';
  // universaalne asendus; kui ei leia, tagastab originaali
  return AXIOM_LINK_TPL.replaceAll('{signature}', signature);
}

// ---- Telegrami saatmine ----
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

// ---- Heliuse sündmuse vormindus + Axiom link ----
function formatHeliusEvent(ev) {
  const wallet    = ev.feePayer || ev.fee_payer || '-';
  const txType    = ev.transaction_type || ev.type || 'UNKNOWN';
  const signature = ev.signature || '-';

  const tt     = Array.isArray(ev.tokenTransfers) && ev.tokenTransfers.length ? ev.tokenTransfers[0] : null;
  const mint   = tt?.mint || '-';
  const amount = tt?.tokenAmount ?? tt?.amount ?? '-';

  const tsMs    = Number(ev.timestamp || 0) * 1000;
  const whenUtc = tsMs ? new Date(tsMs).toISOString().replace('T', ' ').replace('Z', '') : '-';

  const title   = ev.description || 'Solana tehing';

  const lines = [
    `🟣 <b>${title}</b>`,
    `Build: <code>${BUILD}</code>`,
    `Wallet: <code>${wallet}</code>`,
    `Tüüp: <b>${txType}</b>`,
    `Mint: <code>${mint}</code>`,
    `Kogus: <b>${amount}</b>`,
    `Aeg (UTC): ${whenUtc}`,
  ];

  if (signature && signature !== '-') {
    lines.push(`Tx: https://solscan.io/tx/${signature}`);
    const ax = buildAxiomLink(signature);
    if (ax) lines.push(`Axiom: ${ax}`);
  }

  return lines.join('\n');
}

// ---- Health & diag ----
app.get('/', (_req, res) => res.send(`ok (${BUILD})`));

// Näita registreeritud radu (diag)
app.get('/routes', (_req, res) => {
  const routes = [];
  app._router?.stack?.forEach((m) => {
    if (m.route) {
      const methods = Object.keys(m.route.methods).join(',').toUpperCase();
      routes.push(`${methods} ${m.route.path}`);
    }
  });
  res.json({ build: BUILD, routes });
});

// Telegram suitsutest
app.get('/test/telegram', async (_req, res) => {
  try {
    const payload = `✅ Test (${BUILD}) @ ${new Date().toISOString()}`;
    const resp = await sendToTelegram(payload);
    res.status(200).send(resp);
  } catch (e) {
    console.error('❌ /test/telegram error:', e);
    res.status(500).send(String(e));
  }
});

// Lihtne test-sõnumi endpoint (võimaldab oma teksti saata ?text=)
app.get('/test/message', async (req, res) => {
  try {
    const text = (req.query.text || `Ping (${BUILD})`).toString();
    const resp = await sendToTelegram(text);
    res.status(200).send(resp);
  } catch (e) {
    console.error('❌ /test/message error:', e);
    res.status(500).send(String(e));
  }
});

// ---- Helius webhook ----
app.post('/helius', async (req, res) => {
  try {
    if (HELIUS_AUTH) {
      const hdr = req.headers['authorization'];
      if (hdr !== HELIUS_AUTH) {
        console.warn('❌ Wrong Authorization header');
        return res.status(401).send('Unauthorized');
      }
    }

    // Lühike logi
    console.log('🛰️ Headers:', JSON.stringify(req.headers, null, 2));
    console.log('🛰️ Body preview:', JSON.stringify(req.body)?.slice(0, 4000));

    // Vastame KOHE 200
    res.sendStatus(200);

    // Toeta [] ja { data: [] }
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

// ---- Kuula 8080 peal (vastavalt sinu valikule) ----
const HOST = '0.0.0.0';
const PORT = 8080;

app.listen(PORT, HOST, () => {
  console.log(`🚀 Listening on ${HOST}:${PORT} [${BUILD}]`);
});

process.on('SIGTERM', () => {
  console.log('↘️  SIGTERM received, exiting...');
  process.exit(0);
});
