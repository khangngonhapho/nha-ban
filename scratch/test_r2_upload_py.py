import hashlib
import hmac
import datetime
import requests
import json
import os

# Load config
config_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/settings.json"
if os.path.exists(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
        
    r2_access_key = cfg.get("r2_access_key_id")
    r2_secret_key = cfg.get("r2_secret_access_key")
    r2_bucket = cfg.get("r2_bucket_name")
    account_id = cfg.get("cloudflare_account_id")
    r2_public_url = cfg.get("r2_public_url")
    
    print("R2 Config Loaded:")
    print(f"  Access Key ID: {r2_access_key}")
    print(f"  Bucket: {r2_bucket}")
    print(f"  Account ID: {account_id}")
    print(f"  Public URL: {r2_public_url}")
    
    if r2_access_key and r2_secret_key and r2_bucket and account_id:
        def sign_r2_request(data, filename, content_type, access_key, secret_key, bucket, account_id):
            host = f"{bucket}.{account_id}.r2.cloudflarestorage.com"
            endpoint = f"https://{host}"
            key = f"test_uploads/{filename}"
            path = f"/{key}"
            
            t = datetime.datetime.utcnow()
            amz_date = t.strftime('%Y%m%dT%H%M%SZ')
            date_stamp = t.strftime('%Y%m%d')
            
            hashed_payload = hashlib.sha256(data).hexdigest()
            
            canonical_headers = f"host:{host}\nx-amz-content-sha256:{hashed_payload}\nx-amz-date:{amz_date}\n"
            signed_headers = "host;x-amz-content-sha256;x-amz-date"
            
            canonical_request = f"PUT\n{path}\n\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"
            hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
            
            algorithm = "AWS4-HMAC-SHA256"
            region = "auto"
            service = "s3"
            credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
            
            string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashed_canonical_request}"
            
            def sign(key, msg):
                return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
                
            def get_signature_key(key, date_stamp, region_name, service_name):
                k_date = hmac.new(("AWS4" + key).encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
                k_region = sign(k_date, region_name)
                k_service = sign(k_region, service_name)
                k_signing = sign(k_service, "aws4_request")
                return k_signing
                
            signing_key = get_signature_key(secret_key, date_stamp, region, service)
            signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
            
            authorization_header = f"{algorithm} Credential={access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
            
            url = f"{endpoint}{path}"
            headers = {
                'Host': host,
                'Authorization': authorization_header,
                'x-amz-date': amz_date,
                'x-amz-content-sha256': hashed_payload,
                'Content-Type': content_type
            }
            return url, headers

        # Run test
        dummy_content = b"Hello Cloudflare R2! Test upload from BDS-KhangNgo Python script. Time: " + datetime.datetime.now().isoformat().encode('utf-8')
        filename = f"test_py_r2_{int(datetime.datetime.now().timestamp())}.txt"
        
        print(f"\nSigning PUT request for {filename}...")
        url, headers = sign_r2_request(dummy_content, filename, "text/plain", r2_access_key, r2_secret_key, r2_bucket, account_id)
        
        print("Request URL:", url)
        print("Headers:", json.dumps(headers, indent=2))
        
        try:
            print("\nSending PUT request to Cloudflare R2...")
            r = requests.put(url, data=dummy_content, headers=headers, timeout=10)
            print("Status Code:", r.status_code)
            print("Response:", r.text)
            
            if r.status_code == 200:
                print("\nSUCCESS! File uploaded successfully.")
                public_url = f"{r2_public_url}/test_uploads/{filename}"
                print("Public URL to check:", public_url)
            else:
                print("\nFAILED! Server returned error.")
        except Exception as e:
            print("Request failed with error:", e)
    else:
        print("Missing credentials in settings.json")
else:
    print("settings.json not found")
