const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Load credentials
const credsPath = path.join(__dirname, '..', 'credentials.json');
let creds = null;
if (fs.existsSync(credsPath)) {
  creds = JSON.parse(fs.readFileSync(credsPath, 'utf8'));
} else if (process.env.GOOGLE_SERVICE_ACCOUNT_JSON) {
  creds = JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT_JSON);
}

if (!creds) {
  console.error('No credentials.json found and no GOOGLE_SERVICE_ACCOUNT_JSON env var!');
  process.exit(1);
}

async function getGoogleAccessToken(creds) {
  let privateKey = creds.private_key;
  if (privateKey && typeof privateKey === 'string') {
    privateKey = privateKey.replace(/\\n/g, '\n');
  }

  const tokenUri = creds.token_uri || 'https://oauth2.googleapis.com/token';
  const iat = Math.floor(Date.now() / 1000);
  const exp = iat + 3600;

  const header = {
    alg: 'RS256',
    typ: 'JWT'
  };

  const payload = {
    iss: creds.client_email,
    scope: 'https://www.googleapis.com/auth/drive.readonly',
    aud: tokenUri,
    exp: exp,
    iat: iat
  };

  const base64Escape = (str) => {
    return str.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
  };

  const headerB64 = base64Escape(Buffer.from(JSON.stringify(header)).toString('base64'));
  const payloadB64 = base64Escape(Buffer.from(JSON.stringify(payload)).toString('base64'));
  const signatureInput = `${headerB64}.${payloadB64}`;

  const signer = crypto.createSign('RSA-SHA256');
  signer.update(signatureInput);
  const signature = base64Escape(signer.sign(privateKey, 'base64'));

  const jwt = `${signatureInput}.${signature}`;

  const response = await fetch(tokenUri, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
      grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
      assertion: jwt
    }).toString()
  });

  const data = await response.json();
  return data.access_token;
}

async function run() {
  const token = await getGoogleAccessToken(creds);
  if (!token) {
    console.error('Failed to get token');
    return;
  }
  const docId = '1-VlvYmwY9_22dULAF4Xtlooa8A8VUfiV3OVU01OaoGE';
  const url = `https://www.googleapis.com/drive/v3/files/${docId}/export?mimeType=text/plain`;
  const res = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  if (!res.ok) {
    console.error(`Google Docs download failed: ${res.status}`);
    return;
  }
  const text = await res.text();
  console.log('--- DOC CONTENT START ---');
  console.log(text);
  console.log('--- DOC CONTENT END ---');
}

run();
