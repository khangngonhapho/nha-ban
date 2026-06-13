const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// Load settings from settings.json
const settingsPath = path.join(__dirname, '..', 'settings.json');
if (!fs.existsSync(settingsPath)) {
  console.error("settings.json not found!");
  process.exit(1);
}

const cfg = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
const r2AccessKeyId = cfg.r2_access_key_id;
const r2SecretAccessKey = cfg.r2_secret_access_key;
const r2BucketName = cfg.r2_bucket_name;
const cloudflareAccountId = cfg.cloudflare_account_id;
const r2PublicUrl = cfg.r2_public_url;

console.log("R2 Config Loaded:");
console.log(`  Access Key ID: ${r2AccessKeyId}`);
console.log(`  Bucket Name: ${r2BucketName}`);
console.log(`  Account ID: ${cloudflareAccountId}`);
console.log(`  Public URL: ${r2PublicUrl}`);

if (!r2AccessKeyId || !r2SecretAccessKey || !r2BucketName || !cloudflareAccountId) {
  console.error("Missing R2 configuration in settings.json!");
  process.exit(1);
}

function signR2Request(buffer, filename, contentType) {
  const host = `${r2BucketName}.${cloudflareAccountId}.r2.cloudflarestorage.com`;
  const endpoint = `https://${host}`;
  const key = `test_uploads/${filename}`;
  const path = `/${key}`;
  
  const date = new Date();
  const amzDate = date.toISOString().replace(/[:-]/g, '').split('.')[0] + 'Z';
  const dateStamp = amzDate.substring(0, 8);
  
  const hashedPayload = crypto.createHash('sha256').update(buffer).digest('hex');
  
  const canonicalHeaders = `host:${host}\nx-amz-content-sha256:${hashedPayload}\nx-amz-date:${amzDate}\n`;
  const signedHeaders = 'host;x-amz-content-sha256;x-amz-date';
  
  const canonicalRequest = `PUT\n${path}\n\nhost:${host}\nx-amz-content-sha256:${hashedPayload}\nx-amz-date:${amzDate}\n\nhost;x-amz-content-sha256;x-amz-date\n${hashedPayload}`;
  const hashedCanonicalRequest = crypto.createHash('sha256').update(canonicalRequest).digest('hex');
  
  const algorithm = 'AWS4-HMAC-SHA256';
  const region = 'auto';
  const service = 's3';
  const credentialScope = `${dateStamp}/${region}/${service}/aws4_request`;
  
  const stringToSign = `${algorithm}\n${amzDate}\n${credentialScope}\n${hashedCanonicalRequest}`;
  
  // Signature calculation
  const kDate = crypto.createHmac('sha256', 'AWS4' + r2SecretAccessKey).update(dateStamp).digest();
  const kRegion = crypto.createHmac('sha256', kDate).update(region).digest();
  const kService = crypto.createHmac('sha256', kRegion).update(service).digest();
  const kSigning = crypto.createHmac('sha256', kService).update('aws4_request').digest();
  
  const signature = crypto.createHmac('sha256', kSigning).update(stringToSign).digest('hex');
  const authorization = `${algorithm} Credential=${r2AccessKeyId}/${credentialScope}, SignedHeaders=${signedHeaders}, Signature=${signature}`;
  
  return {
    url: `${endpoint}${path}`,
    headers: {
      'Host': host,
      'Authorization': authorization,
      'x-amz-date': amzDate,
      'x-amz-content-sha256': hashedPayload,
      'Content-Type': contentType
    }
  };
}

async function runTest() {
  const dummyContent = "Hello Cloudflare R2! Test upload from BDS-KhangNgo Node.js script. Time: " + new Date().toISOString();
  const buffer = Buffer.from(dummyContent, 'utf8');
  const filename = "test_node_r2_" + Date.now() + ".txt";
  const contentType = "text/plain";
  
  console.log(`\nSigning PUT request for ${filename}...`);
  const reqInfo = signR2Request(buffer, filename, contentType);
  
  console.log("Request URL:", reqInfo.url);
  console.log("Headers:", JSON.stringify(reqInfo.headers, null, 2));
  
  try {
    console.log("\nSending PUT request to Cloudflare R2...");
    const res = await fetch(reqInfo.url, {
      method: 'PUT',
      headers: reqInfo.headers,
      body: buffer
    });
    
    console.log("Status Code:", res.status);
    const text = await res.text();
    console.log("Response text:", text);
    
    if (res.ok) {
      console.log("\nSUCCESS! File uploaded successfully.");
      const publicUrl = `${r2PublicUrl}/test_uploads/${filename}`;
      console.log("Public URL to check:", publicUrl);
    } else {
      console.error("\nFAILED! Server returned error.");
    }
  } catch (err) {
    console.error("Request failed with error:", err);
  }
}

runTest();
