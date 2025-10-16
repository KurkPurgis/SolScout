import express from 'express';
import dotenv from 'dotenv';
// Kui Node 18+ on globaalse fetchiga, node-fetch pole vajalik.
// Kui sul on dependency, võime seda fallback'ina kasutada.
let _fetch = globalThis.fetch;
try {
  if (!_fetch) {
    const { default: nf } = await import('node-fetch');
    _fetch = nf;
  }
} catch (_) {
  /* ignore if node-fetch puudub – Node 18+ katab ära */
}

dotenv.config();

const app = express();

// Parseeri JSON ja ole tolerantne content-type suhtes
app.use(express.json({ type: ['application/json', 'text/plain'], limit: '2mb' }));

// --- abifunktsioon Telegrami saatmiseks ---
async function sendToTelegram(text) {
  const token = process.env.TELEGRAM_TOKEN;
  const chatId = process.env.CHAT_ID;
  if (!token || !chatId) throw new Error('TELEGRAM_TOKEN või CHAT_ID puudub');

  const url = `https://api.telegram.org/bot${token}/sendMessage`;
  const body = {
    chat_id: chatId,
    text,
    parse_mode: 'HTML',
    disable_web_page_preview: true,
  };

  const r = await _fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  const t = await r.text();
  if (!r.ok) throw new Error(`Telegram sendMessage ${r.status}: ${t}`);
  return t;
}

// --- abifunktsioon: Heliuse sündmuse vormindus ---
function formatHeliusEvent(ev) {
  // Helius Enhanced payload (camelCase): description, transaction_type (mõnikord type), feePayer, signature, tokenTransfers, timestamp
  const wallet = ev.feePayer || ev.fee_payer || '-';
  const txType = ev.transaction_type || ev.type || 'UNKNOWN';
  const signature = ev.signature || '-';

  // Proovi leida esimene token transfer (kui on)
  const tt = Array.isArray(ev.tokenTransfers) && ev.tokenTransfers.length ? ev.tokenTransfers[0] : null;
  const mint = tt?.mint || '-';
  const amount = tt?.tokenAmount ?? tt?.amount ?? '-';

  const tsMs = Number(ev.timestamp || 0) * 1000;
  const whenUtc = tsMs ? new Date(tsMs).toISOString().replace('T', ' ').replace('Z', '') : '-';

  const title = ev.description || 'Solana tehing';

  const lines = [
    '🟣 <b>' + title + '</b>',
    `Wallet: <code>${wallet}</code>`,
    `Tüüp: <b>${txType}</b>`,
    `Mint: <code>${mint}</code>`,
    `Kogus: <b>${amount}</b>`,
    `Aeg (UTC): ${whenUtc}`,
  ];

  if (signature && signature !== '-') {
    lines.push(`Tx: https://solscan.io/tx/${signature}`);
  }

  return lines.join('\n');
}

// Health-check
app.get('/', (_req, res) => res.send('ok'));

// Telegram suitsutest
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
    // (valikuline) Authorization header kontroll, kui seadistatud Heliuse dashboardis
    if (process.env.HELIUS_AUTH) {
      const hdr = req.headers['authorization'];
      if (hdr !== process.env.HELIUS_AUTH) {
        console.warn('❌ Wrong Authorization header');
        return res.status(401).send('Unauthorized');
      }
    }

    // --- LOGI LÜHIDALT (ära prindi hiigelkehasid) ---
    const headersPreview = JSON.stringify(req.headers, null, 2);
    const bodyPreview = JSON.stringify(req.body)?.slice(0, 4000);
    console.log('🛰️ Webhook headers:', headersPreview);
    console.log('🛰️ Webhook body preview:', bodyPreview);

    // --- Vastame Heliusele KOHE (väldime timeoute/rettriesid) ---
    res.sendStatus(200);

    // Helius saadab tavaliselt ARRAY juurena; toeta ka legacy { data: [...] }
    const raw = req.body;
    const events = Array.isArray(raw)
      ? raw
      : Array.isArray(raw?.data)
      ? raw.data
      : raw
      ? [raw]
      : [];

    if (!events.length) {
      console.warn('ℹ️ No events in payload');
      return;
    }

    for (const ev of events) {
      try {
        console.log('Processing event signature:', ev?.signature || '-');
        const msg = formatHeliusEvent(ev);
        const tgResp = await sendToTelegram(msg);
        console.log('📨 Telegram OK:', tgResp);
      } catch (err) {
        console.error('❌ Telegram send failed:', err);
      }
    }
  } catch (e) {
    // NB! Siia jõuame vaid enne 200 vastamist tekkinud vigadega; ülal vastasime juba ära.
    console.error('❌ Webhook handler error:', e);
    // ära saada siit uuesti vastust – 200 läks juba välja
  }
});

// Kuula Railway nõutud host/porti
const PORT = process.env.PORT || 8080;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Listening on 0.0.0.0:${PORT}`);
});

// Valikuline: graatsiline sulgemine (näed SIGTERM trassi)
process.on('SIGTERM', () => {
  console.log('↘️  SIGTERM received, exiting...');
  process.exit(0);
});
