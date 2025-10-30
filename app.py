from flask import Flask, request
import requests
from threading import Thread
import time
import random
import re
import traceback

app = Flask(__name__)
app.secret_key = 'debug_2025'

# === FULL ERROR LOG ===
def log_error(msg):
    print(f"\n[ERROR] {msg}")
    traceback.print_exc()

def bomber(cookies_str, gc_ids, messages, prefix, delay, random_delay, limit):
    sent = 0
    session = requests.Session()

    try:
        # === COOKIES PARSE ===
        cookies = {}
        for part in [x.strip() for x in cookies_str.split(';') if x.strip()]:
            if '=' in part:
                k, v = part.split('=', 1)
                cookies[k] = v
        session.cookies.update(cookies)

        if 'c_user' not in cookies or 'xs' not in cookies:
            print("[-] c_user or xs missing in cookies!")
            return

        # === HEADERS ===
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
            'Referer': 'https://m.facebook.com/',
            'Origin': 'https://m.facebook.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml',
            'Connection': 'keep-alive'
        }

        print(f"[+] BOMBER STARTED | c_user: {cookies['c_user']} | GCs: {len(gc_ids)}")

        while limit is None or sent < limit:
            for gc in gc_ids:
                if limit and sent >= limit: break
                for msg in messages:
                    if limit and sent >= limit: break
                    full_msg = f"{prefix} {msg}"

                    try:
                        # === OPEN CHAT ===
                        chat_url = f'https://m.facebook.com/messages/read/?tid=cid.g.{gc}'
                        print(f"[DEBUG] Opening chat: {chat_url}")
                        r = session.get(chat_url, headers=headers, timeout=20)
                        
                        if r.status_code != 200:
                            print(f"[-] Chat open failed: {r.status_code}")
                            continue
                        if 'login' in r.url.lower():
                            print("[-] COOKIES EXPIRED!")
                            return

                        # === EXTRACT fb_dtsg & jazoest ===
                        dtsg = re.search(r'name="fb_dtsg" value="([^"]+)"', r.text)
                        jazo = re.search(r'name="jazoest" value="([^"]+)"', r.text)
                        if not dtsg:
                            print("[-] fb_dtsg NOT FOUND in page!")
                            print(f"[DEBUG] Page snippet: {r.text[:500]}")
                            continue

                        # === SEND MESSAGE ===
                        payload = {
                            'fb_dtsg': dtsg.group(1),
                            'jazoest': jazo.group(1) if jazo else '',
                            'body': full_msg,
                            'tids': f'cid.g.{gc}',
                            'ids[0]': gc,
                            'wwwupp': 'C3'
                        }

                        send_url = 'https://m.facebook.com/messages/send/'
                        print(f"[DEBUG] Sending to {send_url}")
                        r2 = session.post(send_url, data=payload, headers=headers, timeout=20)

                        if r2.status_code == 200 and ('success' in r2.text or 'sent' in r2.text.lower()):
                            sent += 1
                            print(f"[+] SENT [{sent}] → {full_msg}")
                        else:
                            print(f"[-] SEND FAILED → Status: {r2.status_code}")
                            print(f"[DEBUG] Response: {r2.text[:300]}")

                    except Exception as e:
                        log_error(f"Send error: {e}")

                    time.sleep(random.uniform(5, 10) if random_delay else delay)

    except Exception as e:
        log_error(f"Bomber crashed: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            cookies = request.form.get('cookies', '').strip()
            if not cookies or len(cookies) < 50:
                return error("Cookies too short!")

            file = request.files.get('txtFile')
            if not file:
                return error("No file uploaded!")
            messages = [l.strip() for l in file.read().decode('utf-8', 'ignore').splitlines() if l.strip()]
            if not messages:
                return error("Messages empty!")

            gc_ids = [g.strip() for g in request.form.get('gc', '').split(',') if g.strip()]
            if not gc_ids:
                return error("GC ID missing!")

            prefix = request.form.get('prefix', 'LEGEND')
            delay = max(5, int(request.form.get('delay', '6')))
            random_delay = 'random' in request.form
            limit = request.form.get('limit')
            limit = int(limit) if limit and limit.isdigit() else None

            print(f"[INFO] Starting bomber with {len(gc_ids)} GC(s) and {len(messages)} message(s)")
            Thread(target=bomber, args=(cookies, gc_ids, messages, prefix, delay, random_delay, limit), daemon=True).start()
            return success("BOMBING STARTED! Check terminal for logs.")

        except Exception as e:
            log_error(f"Form error: {e}")
            return error("Form processing failed!")

    return '''
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>COOKIES BOMBER DEBUG</title>
    <style>
      body{background:#000;color:#0f0;font-family:Courier;text-align:center;padding:20px;}
      .box{background:#111;border:1px solid #0f0;padding:18px;border-radius:10px;margin:15px auto;max-width:500px;}
      textarea, input, button{width:100%;padding:14px;margin:10px 0;background:#000;border:1px solid #0f0;color:#0f0;border-radius:8px;}
      button{background:#0f0;color:#000;font-weight:bold;}
      h1{text-shadow:0 0 25px #0f0;}
    </style></head><body>
    <h1>COOKIES BOMBER [DEBUG]</h1>
    <form method="post" enctype="multipart/form-data">
      <div class="box"><textarea name="cookies" rows="5" placeholder="c_user=...; xs=..." required></textarea></div>
      <div class="box"><input type="file" name="txtFile" required></div>
      <div class="box"><input type="text" name="gc" placeholder="GC ID" required></div>
      <div class="box"><input type="text" name="prefix" value="LEGEND"></div>
      <div class="box"><input type="number" name="delay" value="6" min="5"></div>
      <div class="box"><input type="checkbox" name="random"> Random Delay</div>
      <div class="box"><input type="number" name="limit" placeholder="Stop after"></div>
      <button>START</button>
    </form>
    <div class="box"><small>Check TERMINAL for full logs!</small></div>
    </body></html>
    '''

def error(msg): 
    return f'<div style="background:#000;color:#f00;padding:50px;text-align:center;"><h2>ERROR</h2><p>{msg}</p><a href="/" style="color:#0f0;">BACK</a></div>'

def success(msg): 
    return f'<div style="background:#000;color:#0f0;padding:50px;text-align:center;"><h2>SUCCESS</h2><p>{msg}</p><a href="/" style="color:#0f0;">BACK</a></div>'

if __name__ == '__main__':
    print("DEBUG BOMBER STARTED → http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
