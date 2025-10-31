from flask import Flask, request, jsonify
import requests
from threading import Thread
import time
import random
import re

app = Flask(__name__)
app.secret_key = 'perfect_2025'

logs = []

def add_log(msg):
    logs.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
    if len(logs) > 500: logs.pop(0)

def bomber(cookies_str, gc_ids, messages, prefix, delay, random_delay, limit):
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

    add_log(f"ON | c_user: {cookies.get('c_user')}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        'Referer': 'https://m.facebook.com/',
        'Origin': 'https://m.facebook.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest'
    }

    # === GET fb_dtsg FROM MOBILE HOME (CORRECT WAY) ===
    home = session.get('https://m.facebook.com/', headers=headers, timeout=20)
    if 'login' in home.url.lower():
        add_log("COOKIES DEAD!")
        return

    # CORRECT REGEX FOR MOBILE
    dtsg = (
        re.search(r'data-dtsg="([^"]+)"', home.text) or
        re.search(r'"dtsg":{"token":"([^"]+)"', home.text) or
        re.search(r'"token":"([^"]+)"', home.text)
    )
    if not dtsg:
        add_log("fb_dtsg NOT FOUND! But cookies alive.")
        return
    fb_dtsg = dtsg.group(1)

    add_log(f"fb_dtsg FOUND: {fb_dtsg[:8]}...")

    # === SEND MESSAGE ===
    while limit is None or sent < limit:
        for gc in gc_ids:
            if limit and sent >= limit: break
            for msg in messages:
                if limit and sent >= limit: break
                full_msg = f"{prefix} {msg}"

                try:
                    payload = {
                        'fb_dtsg': fb_dtsg,
                        'tids': f'cid.g.{gc}',  # GROUP CHAT
                        'body': full_msg,
                        'wwwupp': 'C3'
                    }

                    send_url = 'https://m.facebook.com/messages/send/'
                    r = session.post(send_url, data=payload, headers=headers, timeout=20)

                    if r.status_code == 200 and 'error' not in r.text.lower():
                        sent += 1
                        add_log(f"SENT [{sent}] → {full_msg}")
                    else:
                        add_log(f"FAILED → Check GC ID")

                except Exception as e:
                    add_log(f"ERROR: {str(e)[:40]}")

                time.sleep(random.uniform(6, 13) if random_delay else delay)

# === SAME HTML AS BEFORE ===
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            cookies = request.form.get('cookies', '').strip()
            if 'c_user' not in cookies or 'xs' not in cookies:
                return error("c_user/xs missing!")

            file = request.files['txtFile']
            messages = [l.strip() for l in file.read().decode('utf-8', 'ignore').splitlines() if l.strip()]
            if not messages: return error("Messages empty!")

            gc_ids = [g.strip() for g in request.form.get('gc', '').split(',') if g.strip()]
            if not gc_ids: return error("GC ID daalo!")

            prefix = request.form.get('prefix', 'LEGEND')
            delay = max(6, int(request.form.get('delay', '8')))
            random_delay = 'random' in request.form
            limit = int(request.form.get('limit')) if request.form.get('limit') else None

            add_log("BOMBING LIVE! SCRIPT FIXED!")
            Thread(target=bomber, args=(cookies, gc_ids, messages, prefix, delay, random_delay, limit), daemon=True).start()
            return success("BOMBING CHAL GAYA!")

        except Exception as e:
            add_log(f"ERROR: {e}")
            return error("Form failed!")

    return '''
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>PERFECT v11</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body{background:#000;color:#0f0;font-family:Courier;text-align:center;padding:20px;}
      .box{background:#111;border:1px solid #0f0;padding:18px;border-radius:10px;margin:15px auto;max-width:500px;}
      textarea, input, button{width:100%;padding:14px;margin:10px 0;background:#000;border:1px solid #0f0;color:#0f0;border-radius:8px;}
      button{background:#0f0;color:#000;font-weight:bold;}
      h1{text-shadow:0 0 25px #0f0;}
      #console{background:#000;color:#0f0;padding:15px;height:280px;overflow-y:scroll;border:1px solid #0f0;margin:20px auto;max-width:500px;font-size:13px;text-align:left;}
    </style></head><body>
    <h1>PERFECT BOMBER v11</h1>
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
    <div id="console">LIVE CONSOLE...</div>
    <script>
      setInterval(() => {
        fetch('/logs').then(r => r.json()).then(d => {
          document.getElementById('console').innerHTML = d.logs.join('<br>');
          document.getElementById('console').scrollTop = document.getElementById('console').scrollHeight;
        });
      }, 1000);
    </script>
    </body></html>
    '''

@app.route('/logs')
def get_logs():
    return jsonify({'logs': logs})

def error(m): return f'<div style="color:#f00;background:#000;padding:50px;text-align:center;"><h2>ERROR</h2><p>{m}</p><a href="/" style="color:#0f0;">BACK</a></div>'
def success(m): return f'<div style="color:#0f0;background:#000;padding:50px;text-align:center;"><h2>SUCCESS</h2><p>{m}</p><a href="/" style="color:#0f0;">BACK</a></div>'

if __name__ == '__main__':
    print("PERFECT v11 → http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, threaded=True)
