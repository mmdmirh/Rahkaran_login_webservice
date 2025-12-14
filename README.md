# Rahkaran Authentication Library

A Python library for authenticating to Rahkaran ERP system via its web service.

## Overview

This library handles the full authentication flow for Rahkaran ERP systems:
1. **GET** login page to obtain session tokens and RSA public key
2. **Encrypt** password using RSA (sessionid + "--" + password)
3. **POST** login form with encrypted credentials
4. **Return** authentication cookies for subsequent API calls

## Requirements

- **Python 3.7+**
- **Node.js** (required for RSA encryption)
- **requests** library

## Installation

```bash
# Clone the repository
git clone https://github.com/mmdmirh/Rahkaran_login_webservice.git
cd Rahkaran_login_webservice

# Install Python dependencies
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install .
```

## Usage

### Basic Usage

```python
from rahkaran_auth import RahkaranAuth

# Create auth client
auth = RahkaranAuth()

# Login
result = auth.login(
    base_url="https://your-company.rahkaran.ir/sg3g/xxxxxxxx",
    username="your_username",
    password="your_password"
)

# Check result
if result["success"]:
    print("Login successful!")
    print(f"Auth token: {result['cookies']['sg-auth-sg']}")
else:
    print(f"Login failed: {result['error']}")
```

### Using Cookies in API Requests

```python
import requests
from rahkaran_auth import RahkaranAuth

auth = RahkaranAuth()
result = auth.login(
    base_url="https://your-company.rahkaran.ir/sg3g/xxxxxxxx",
    username="your_username",
    password="your_password"
)

if result["success"]:
    # Option 1: Use cookie_header string
    headers = {"Cookie": result["cookie_header"]}
    response = requests.get("https://your-company.rahkaran.ir/sg3g/xxxxxxxx/api/endpoint", headers=headers)
    
    # Option 2: Use cookies dict
    session = requests.Session()
    session.cookies.update(result["cookies"])
    response = session.get("https://your-company.rahkaran.ir/sg3g/xxxxxxxx/api/endpoint")
```

### Using with cURL

```bash
curl 'https://your-company.rahkaran.ir/sg3g/xxxxxxxx/api/endpoint' \
  -H 'Cookie: sg-auth-sg=YOUR_TOKEN; TS01aeaf51=YOUR_SESSION; sg-dummy=-'
```

## API Reference

### `RahkaranAuth(scripts_dir=None)`

Initialize the authentication client.

**Parameters:**
- `scripts_dir` (str, optional): Directory containing RSA JS files. Defaults to the package directory.

### `login(base_url, username, password) -> dict`

Authenticate to the Rahkaran system.

**Parameters:**
- `base_url` (str): Base URL of the Rahkaran system (e.g., `https://company.rahkaran.ir/sg3g/xxxxxxxx`)
- `username` (str): Login username
- `password` (str): Login password

**Returns:**
```python
{
    "success": True,              # Whether login succeeded
    "cookies": {
        "sg-auth-sg": "...",      # Authentication token (main auth cookie)
        "TS01aeaf51": "...",      # Session/load balancer cookie
        "sg-dummy": "-"           # Placeholder cookie
    },
    "cookie_header": "...",       # Ready-to-use Cookie header string
    "error": None                 # Error message if login failed
}
```

## Authentication Flow

```
┌─────────────────────────────────────────────────────────────┐
│  HANDSHAKE 1: GET /Authentication/Login.aspx               │
│  ───────────────────────────────────────────────────────── │
│  Returns: __VIEWSTATE, rsa_e, rsa_m, sessionid             │
└─────────────────────────────────────────────────────────────┘
                              ↓
              Encrypt: sessionid + "--" + password
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  HANDSHAKE 2: POST /Authentication/Login.aspx              │
│  ───────────────────────────────────────────────────────── │
│  Returns: sg-auth-sg cookie (auth token)                   │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
├── rahkaran_auth.py    # Main authentication class
├── rsa_encrypt.js      # Node.js RSA encryption helper
├── BigInt.js           # BigInt library for RSA
├── Barrett.js          # Barrett reduction for RSA
├── RSA.js              # RSA encryption library
├── requirements.txt    # Python dependencies
├── setup.py            # Package setup
└── README.md           # This file
```

## Notes

- The RSA encryption uses the actual JavaScript libraries from the Rahkaran login page for 100% compatibility
- Node.js is required to run the RSA encryption (called as a subprocess)
- Session cookies should be refreshed periodically as they expire

## License

MIT License
