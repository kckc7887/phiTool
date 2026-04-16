# phiTool - Phigros 数据管理工具
# Copyright (C) 2026 Chnynnya
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import hashlib
import hmac
import json
import random
import string
import sys
import time
import urllib.parse

import aiohttp

# TapTap OAuth 配置
TAPTAP_CLIENT_ID = "rAK3FfdieFob2Nn8Am"
TAPTAP_SCOPE = "public_profile"
TAPTAP_PLATFORM = "unity"

# LeanCloud 配置
LC_CLIENT_ID = "rAK3FfdieFob2Nn8Am"
LC_APP_KEY = "Qr9AEqtuoSVS3zeD6iVbM4ZC0AtkJcQ89tywVyi0"
LC_SERVER_URL = "https://rak3ffdi.cloud.tds1.tapapis.cn"

async def generate_device_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

async def request_device_code(session):
    device_id = await generate_device_id()
    url = "https://accounts.tapapis.cn/oauth2/v1/device/code"
    
    data = {
        "client_id": TAPTAP_CLIENT_ID,
        "response_type": "device_code",
        "scope": TAPTAP_SCOPE,
        "platform": TAPTAP_PLATFORM,
        "info": json.dumps({"device_id": device_id})
    }
    
    async with session.post(url, data=data) as response:
        return await response.json(), device_id

async def check_token_status(session, device_code, device_id):
    url = "https://accounts.tapapis.cn/oauth2/v1/token"
    
    data = {
        "grant_type": "device_token",
        "client_id": TAPTAP_CLIENT_ID,
        "code": device_code,
        "info": json.dumps({"device_id": device_id})
    }
    
    async with session.post(url, data=data) as response:
        return await response.json()

def build_mac_authorization(url, method, kid, mac_key):
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port or 443
    uri = parsed_url.path
    if parsed_url.query:
        uri += "?" + parsed_url.query
    
    timestamp = str(int(time.time())).zfill(10)
    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    signature_base = f"{timestamp}\n{nonce}\n{method}\n{uri}\n{host}\n{port}\n\n"
    
    import base64

    signature = hmac.new(
        mac_key.encode(),
        signature_base.encode(),
        hashlib.sha1
    ).digest()
    
    mac = base64.b64encode(signature).decode()
    
    return f'MAC id="{kid}", ts="{timestamp}", nonce="{nonce}", mac="{mac}"'

async def get_profile(session, token_data):
    url = f"https://open.tapapis.cn/account/profile/v1?client_id={TAPTAP_CLIENT_ID}"
    
    authorization = build_mac_authorization(
        url,
        "GET",
        token_data["kid"],
        token_data["mac_key"]
    )
    
    headers = {"Authorization": authorization}
    
    async with session.get(url, headers=headers) as response:
        return await response.json()

async def exchange_session_token(session, profile, token_data):
    url = f"{LC_SERVER_URL}/1.1/users"
    
    timestamp = str(int(time.time()))
    lc_sign = hashlib.md5(f"{timestamp}{LC_APP_KEY}".encode()).hexdigest()
    lc_sign = f"{lc_sign},{timestamp}"
    
    auth_data = {
        "taptap": {
            "openid": profile["data"]["openid"],
            "name": profile["data"]["name"],
            "avatar": profile["data"]["avatar"],
            "kid": token_data["kid"],
            "access_token": token_data["access_token"],
            "mac_key": token_data["mac_key"],
            "expires_in": token_data.get("expires_in", 0),
            "platform": "TapTap"
        }
    }
    
    headers = {
        "X-LC-Id": LC_CLIENT_ID,
        "X-LC-Sign": lc_sign,
        "Content-Type": "application/json"
    }
    
    async with session.post(url, headers=headers, json={"authData": auth_data}) as response:
        result = await response.json()
        return result.get("sessionToken")

async def taptap_qr_login():
    async with aiohttp.ClientSession() as session:
        sys.stderr.write("[*] 请求设备码...\n")
        device_code_response, device_id = await request_device_code(session)
        
        if not device_code_response.get("success"):
            print(json.dumps({"error": f"获取设备码失败: {device_code_response}", "code": 1}))
            return
        
        data = device_code_response.get("data", {})
        device_code = data.get("device_code")
        qrcode_url = data.get("qrcode_url", "")
        expires_in = data.get("expires_in", 300)
        
        if not device_code:
            print(json.dumps({"error": "响应中缺少 device_code 字段", "code": 2}))
            return
        
        sys.stderr.write(f"[*] 二维码: {qrcode_url}\n")
        sys.stderr.write(f"[*] 二维码有效期：{expires_in} 秒\n")
        sys.stderr.write("[*] 等待用户扫码...\n")
        
        start_time = time.time()
        while time.time() - start_time < expires_in:
            await asyncio.sleep(2)
            
            result = await check_token_status(session, device_code, device_id)
            
            if result.get("success"):
                sys.stderr.write("[+] 用户已确认登录！\n")
                token_data = result["data"]
                
                sys.stderr.write("[*] 获取用户信息...\n")
                profile = await get_profile(session, token_data)
                
                sys.stderr.write("[*] 换取 sessionToken...\n")
                session_token = await exchange_session_token(session, profile, token_data)
                
                if session_token:
                    print(json.dumps({"session_token": session_token, "expires_in": 0}))
                    return
                else:
                    print(json.dumps({"error": "换取 sessionToken 失败", "code": 3}))
                    return
                    
            else:
                data = result.get("data", {})
                error = data.get("error")
                if error == "authorization_pending":
                    sys.stderr.write("[*] 等待扫描...\n")
                elif error == "authorization_waiting":
                    sys.stderr.write("[*] 用户已扫描，请确认登录...\n")
                elif error:
                    print(json.dumps({"error": f"登录失败: {error}", "code": 4}))
                    return
                else:
                    print(json.dumps({"error": f"未知错误: {result}", "code": 5}))
                    return
        
        print(json.dumps({"error": "二维码已过期", "code": 6}))

if __name__ == "__main__":
    asyncio.run(taptap_qr_login())