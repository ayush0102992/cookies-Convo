from flask import Flask, request
import requests
from threading import Thread
import time
import random
import re

app = Flask(__name__)
app.secret_key = 'send_2025'

def send_bomb(cookies_str, gc_ids, messages, prefix, delay, random_delay, limit):
    sent = 0
    session = requests.Session()

    # === COOKIES ===
    cookies = {}
    for p in cookies_str.split(';'):
        p = p.strip()
        if '=' in p:
            k, v = p.split('=', 1)
            cookies[k] = v
    session.cookies.update(cookies)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        'Referer': 'https://m.facebook.com/',
        'Origin': 'https://m.facebook.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive'
    }

    print(f"[+] BOMBER LIVE | c_user: {cookies.get('c_user','?')}")

    while limit is None or sent < limit:
        for gc in gc_ids:
            if limit and sent >= limit: break
            for msg in messages:
                if limit and sent >= limit: break
                full_msg = f"{prefix} {msg}"

                try:
                    # === STEP 1: Open Chat + Get fb_dtsg ===
                    chat_url = f'https://m.facebook.com/messages/thread/{gc}/'
                    r1 = session.get(chat_url, headers=headers, timeout=20)
                    if 'login' in r1.url.lower():
                        print("[-] COOKIES EXPIRED!")
                        return

                    # === EXTRACT fb_dtsg & jazoest (NEW PATTERN) ===
                    dtsg = re.search(r'"fb_dtsg":"([^"]+)"', r1.text) or re.search(r'name="fb_dtsg" value="([^"]+)"', r1.text)
                    jazo = re.search(r'"jazoest":"([^"]+)"', r1.text) or re.search(r'name="jazoest" value="([^"]+)"', r1.text)
                    if not dtsg:
                        print("[-] fb_dtsg NOT FOUND!")
                        continue

                    # === STEP 2: SEND MESSAGE (NEW ENDPOINT) ===
                    payload = {
                        'fb_dtsg': dtsg.group(1),
                        'jazoest': jazo.group(1) if jazo else '',
                        'body': full_msg,
                        'send': 'Send',
                        'tids': f'cid.c.{gc}:0',
                        'wwwupp': 'C3',
                        'referrer': 'thread',
                        'ctype': '',
                        'cver': 'legacy',
                        'rst_icv': ''
                    }

                    send_url = f'https://m.facebook.com/messages/send/?icid=uf_bar&entrypoint=uf_bar'
                    r2 = session.post(send_url, data=payload, headers=headers, timeout=20)

                    if r2.status_code == 200 and ('"success":true' in r2.text or 'message_sent' in r2.text):
                        sent += 1
                        print(f"[+] SENT [{sent}] → {full_msg} | GC: {gc}")
                    else:
                        print(f"[-] FAILED → {r2.status_code}")

                except Exception as e:
                    print(f"[-] ERROR: {e}")

                time.sleep(random.uniform(6, 12) if random_delay else delay)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        cookies = request.form.get('cookies', '').strip()
        if not cookies or 'c_user' not in cookies:
            return error("Cookies Invalid!")

        file = request.files['txtFile']
        messages = [l.strip() for l in file.read().decode('utf-8', 'ignore').splitlines() if l.strip()]
        if not messages:
            return error("Messages Empty!")

        gc_ids = [g.strip() for g in request.form.get('gc', '').split(',') if g.strip()]
        if not gc_ids:
            return error("GC ID Daalo!")

        prefix = request.form.get('prefix', 'LEGEND')
        delay = max(6, int(request.form.get('delay', '8')))
        random_delay = 'random' in request.form
        limit = int(request.form.get('limit')) if request.form.get('limit') else None

        Thread(target=send_bomb, args=(cookies, gc_ids, messages, prefix, delay, random_delay, limit), daemon=True).start()
        return success("BOMBING CHAL RAHA HAI! Check terminal.")

    return '''
    <!DOCTYPE html>
    <html><head><title>COOKIES BOMBER SEND</title>
    <style>
      body{background:#000;color:#0f0;font-family:Courier;text-align:center;padding:20px;}
      .box{background:#111;border:1px solid #0f0;padding:18px;border-radius:10px;margin:15px auto;max-width:500px;}
      textarea, input, button{width:100%;padding:14px;margin:10px 0;background:#000;border:1px solid #0f0;color:#0f0;border-radius:8px;}
      button{background:#0f0;color:#000;font-weight:bold;}
      h1{text-shadow:0 0 25px #0f0;}
    </style></head><body>
    <h1>COOKIES BOMBER [SEND]</h1>
    <form method="post" enctype="multipart/form-data">
      <div class="box"><textarea name="cookies" rows="5" placeholder="c_user=...; xs=..." required></textarea></div>
      <div class="box"><input type="file" name="txtFile" required></div>
      <div class="box"><input type="text" name="gc" placeholder="GC ID" required></div>
      <div class="box"><input type="text" name="prefix" value="LEGEND"></div>
      <div class="box"><input type="number" name="delay" value="8" min="6"></div>
      <div class="box"><input type="checkbox" name="random"> Random Delay</div>
      <div class="box"><input type="number" name="limit" placeholder="Stop after"></div>
      <button>START BOMBING</button>
    </form>
    <div class="box"><small>Check TERMINAL for sent logs!</small></div>
    </body></html>
    '''

def error(m): return f'<div style="color:#f00;background:#000;padding:50px;text-align:center;"><h2>ERROR</h2><p>{m}</p><a href="/" style="color:#0f0;">BACK</a></div>'
def success(m): return f'<div style="color:#0f0;background:#000;padding:50px;text-align:center;"><h2>SUCCESS</h2><p>{m}</p><a href="/" style="color:#0f0;">BACK</a></div>'

if __name__ == '__main__':
    print("SEND BOMBER → http://localhost:5000")
    app.run(host='0.0.0.0', port=5000)
