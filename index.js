// index.js — SolScout / Railway / 8080 + Axiom & Jupiter lingid

import express from 'express';

// Devis lubame .env; Railway-s pole vaja
if (process.env.NODE_ENV !== 'production') {
  try {
    const { default: dotenv } = await import('dotenv');
    dotenv.config();
  } catch (_) {
    // ignore if dotenv not installed
  }
}

const app = express();
app.use(express.json({ type: ['application/json', 'text/plain'], limit: '2mb' }));

// ---- Keskkonnamuutujad (trim) ----
const TOKEN      = (process.env.TELEGRAM_TOKEN || '').trim();
const CHATID     = (process.env.CHAT_ID || '').trim();
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

// ---- Heliuse sündmuse vormindus + Axiom/Jupiter lingid ----
// watchedWallet: aadress, mille vaates otsime "positiivset sissevoolu" (ostetud tokenit)
function formatHeliusEvent(ev, watchedWallet) {
  const wallet    = ev.feePayer || ev.fee_payer || '-';
  const txType    = ev.transaction_type || ev.type || 'UNKNOWN';
  const signature = ev.signature || '-';

  // Proovi leida OSTETUD token: tokenTransfer, kus kasutaja sai positiivse koguse
  let boughtTT = null;
  if (Array.isArray(ev.tokenTransfers) && ev.tokenTransfers.length) {
    const self = watchedWallet || wallet;
    boughtTT = ev.tokenTransfers.find(t => {
      const amt = Number(t.tokenAmount ?? t.amount ?? 0);
      const ua  = t.userAccount || t.toUserAccount || t.owner;
      return ua === self && amt > 0;
    });
    // Fallback: kui ei leitud üheselt, võta esimene transfer
    if (!boughtTT) boughtTT = ev.tokenTransfers[0];
  }

  const mint   = boughtTT?.mint || '-';
  const amount = boughtTT?.tokenAmount ?? boughtTT?.amount ?? '-';

  const tsMs    = Number(ev.timestamp || 0) * 1000;
  const whenUtc = tsMs ? new Date(tsMs).toISOString().replace('T', ' ').replace('Z', '') : '-';

  const title   = ev.description || 'Solana tehing';

  // Linkide koostamine
  const axiomUrl   = (mint && mint !== '-') ? `https://axiom.trade/meme/${mint}` : '';
  const jupSolUrl  = (mint && mint !== '-') ? `https://jup.ag/swap/SOL-${mint}`   : '';
  const jupUsdcUrl = (mint && mint !== '-') ? `https://jup.ag/swap/USDC-${mint}` : '';

  const lines = [
    '🟣 <b>' + title + '</b>',
    `Wallet: <code>${wallet}</code>`,
    `Tüüp: <b>${txType}</b>`,
    `Mint: <code>${mint}</code>`,
    `Kogus: <b>${amount}</b>`,
    `Aeg (UTC): ${whenUtc}`,
  ];

  if (signature && signature !== '-') {
    lines.push(`Tx: https://solscan.io/tx/${signature}solscan</a>`);
  }

  if (mint && mint !== '-') {
    if (axiomUrl)   lines.push(`Axiom: ${axiomUrl}ava</a>`);
    if (jupSolUrl)  lines.push(`Jupiter (SOL): ${jupSolUrl}swap</a>`);
    if (jupUsdcUrl) lines.push(`Jupiter (USDC): ${jupUsdcUrl}swap</a>`);
  }

  return lines.join('\n');
}

// ---- Health ----
app.get('/', (_req, res) => res.send('ok'));

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

// (valikuline) Diagnoos: näita registreeritud radu
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

    // Logi lühidalt
    console.log('🛰️ Headers:', JSON.stringify(req.headers, null, 2));
    console.log('🛰️ Body preview:', JSON.stringify(req.body)?.slice(0, 4000));

    // Vastame KOHE, siis töötleme taustal
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
        const msg = formatHeliusEvent(ev, ev.feePayer);
        const tg  = await sendToTelegram(msg);
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
