import os
import json
import time
import urllib.request
import urllib.parse
import base64

def get_creds():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    env_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if env_json:
        return json.loads(env_json)
    return None

def base64_escape(s):
    return s.replace('+', '-').replace('/', '_').replace('=', '')

def sign_jwt(private_key_pem, message):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None
    )
    signature = private_key.sign(
        message.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64_escape(base64.b64encode(signature).decode('utf-8'))

def get_google_access_token(creds):
    private_key = creds['private_key']
    private_key = private_key.replace('\\n', '\n')
    
    token_uri = creds.get('token_uri', 'https://oauth2.googleapis.com/token')
    iat = int(time.time())
    exp = iat + 3600
    
    header = {
        "alg": "RS256",
        "typ": "JWT"
    }
    
    payload = {
        "iss": creds['client_email'],
        "scope": "https://www.googleapis.com/auth/drive.readonly",
        "aud": token_uri,
        "exp": exp,
        "iat": iat
    }
    
    def b64_encode(obj):
        return base64_escape(base64.b64encode(json.dumps(obj).encode('utf-8')).decode('utf-8'))
        
    header_b64 = b64_encode(header)
    payload_b64 = b64_encode(payload)
    signature_input = f"{header_b64}.{payload_b64}"
    
    sig = sign_jwt(private_key, signature_input)
    jwt = f"{signature_input}.{sig}"
    
    data = urllib.parse.urlencode({
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'assertion': jwt
    }).encode('utf-8')
    
    req = urllib.request.Request(token_uri, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode('utf-8'))
        return res_data['access_token']

def run():
    creds = get_creds()
    if not creds:
        print("No credentials.json found!")
        return
        
    try:
        token = get_google_access_token(creds)
    except Exception as e:
        print(f"Error getting token: {e}")
        return
        
    doc_id = '1-VlvYmwY9_22dULAF4Xtlooa8A8VUfiV3OVU01OaoGE'
    url = f"https://www.googleapis.com/drive/v3/files/{doc_id}/export?mimeType=text/plain"
    
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    try:
        with urllib.request.urlopen(req) as response:
            text = response.read().decode('utf-8')
            if text.startswith('\ufeff'):
                text = text[1:]
            out_path = os.path.join(os.path.dirname(__file__), 'doc_content.txt')
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print("Successfully written to scratch/doc_content.txt")
    except Exception as e:
        print(f"Error fetching doc: {e}")

if __name__ == '__main__':
    run()
