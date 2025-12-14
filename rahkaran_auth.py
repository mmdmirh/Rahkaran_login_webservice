"""
Rahkaran Authentication Library
================================
A reusable authentication class for the Rahkaran system.

Usage:
    from rahkaran_auth import RahkaranAuth
    
    auth = RahkaranAuth()
    result = auth.login(
        base_url="https://example.rahkaran.ir/sg3g/xxx",
        username="user",
        password="pass"
    )
    
    if result["success"]:
        print(result["cookie_header"])  # Use in API calls
"""

import re
import subprocess
from pathlib import Path
import requests


class RahkaranAuth:
    """Authentication client for Rahkaran system."""
    
    def __init__(self, scripts_dir: str = None):
        """
        Initialize the authentication client.
        
        Args:
            scripts_dir: Directory containing RSA JS files. Defaults to same dir as this file.
        """
        self.scripts_dir = Path(scripts_dir) if scripts_dir else Path(__file__).parent
    
    def _extract_field(self, html: str, field_name: str) -> str:
        """Extract a hidden field value from HTML."""
        patterns = [
            rf'name="{field_name}"[^>]*value="([^"]*)"',
            rf'id="{field_name}"[^>]*value="([^"]*)"',
        ]
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(1)
        return ""
    
    def _encrypt_password(self, password: str, rsa_e: str, rsa_m: str, session_id: str) -> str:
        """
        Encrypt password using Node.js RSA implementation.
        Password is encrypted as: sessionid + "--" + password
        """
        script_path = self.scripts_dir / "rsa_encrypt.js"
        
        if not script_path.exists():
            raise FileNotFoundError(f"RSA encryption script not found: {script_path}")
        
        result = subprocess.run(
            ['node', str(script_path), password, rsa_e, rsa_m, session_id],
            cwd=str(self.scripts_dir),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"RSA encryption failed: {result.stderr}")
        
        return result.stdout.strip()
    
    def login(self, base_url: str, username: str, password: str) -> dict:
        """
        Authenticate to Rahkaran and return session info.
        
        Args:
            base_url: Base URL of the Rahkaran system (e.g., https://example.rahkaran.ir/sg3g/xxx)
            username: Login username
            password: Login password
        
        Returns:
            dict with:
                - success: bool
                - cookies: dict of cookie name -> value
                - cookie_header: string ready for HTTP Cookie header
                - error: string (if failed)
        """
        login_url = f"{base_url.rstrip('/')}/Authentication/Login.aspx"
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        })
        
        result = {
            "success": False,
            "cookies": {},
            "cookie_header": "",
            "error": None
        }
        
        try:
            # HANDSHAKE 1: GET login page for tokens
            response = session.get(login_url)
            if response.status_code != 200:
                result["error"] = f"GET failed: HTTP {response.status_code}"
                return result
            
            html = response.text
            viewstate = self._extract_field(html, '__VIEWSTATE')
            viewstate_gen = self._extract_field(html, '__VIEWSTATEGENERATOR')
            event_validation = self._extract_field(html, '__EVENTVALIDATION')
            rsa_e = self._extract_field(html, 'rsa_e')
            rsa_m = self._extract_field(html, 'rsa_m')
            session_id = self._extract_field(html, 'sessionid')
            
            if not all([viewstate, rsa_e, rsa_m, session_id]):
                result["error"] = "Failed to extract tokens from login page"
                return result
            
            # Encrypt password: sessionid--password
            hashed_password = self._encrypt_password(password, rsa_e, rsa_m, session_id)
            
            # HANDSHAKE 2: POST login form
            import uuid
            post_data = {
                'uid': str(uuid.uuid4()),
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': viewstate,
                '__VIEWSTATEGENERATOR': viewstate_gen,
                '__EVENTVALIDATION': event_validation,
                'txtUsername': username,
                'txtPassword': '',
                'btnSubmit': 'Submit',
                'rsa_e': rsa_e,
                'rsa_m': rsa_m,
                'sessionid': session_id,
                'hashedPassword': hashed_password,
                'errorMessage': '',
            }
            
            # Extract origin from base_url
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            origin = f"{parsed.scheme}://{parsed.netloc}"
            
            response = session.post(
                login_url,
                data=post_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Origin': origin,
                    'Referer': login_url,
                },
                allow_redirects=True
            )
            
            # Check success
            if 'Login.aspx' not in response.url:
                result["success"] = True
                result["cookies"] = session.cookies.get_dict()
                result["cookie_header"] = "; ".join(
                    f"{k}={v}" for k, v in result["cookies"].items()
                )
            else:
                error_msg = self._extract_field(response.text, 'errorMessage')
                result["error"] = error_msg or "Login failed"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
