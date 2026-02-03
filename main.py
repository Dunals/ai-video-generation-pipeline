import requests
import json
import uuid
import os
import random
import time
import concurrent.futures

SPACE_URL = "https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space"
IMAGE_PATH = "1.jpg"
OUTPUT_FILENAME = "final_output_video.mp4"

PROXY_SOURCES = [
   "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
    "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt"
]

THREAD_COUNT = 300      
PROXY_CHECK_TIMEOUT = 5

def get_all_proxies():
    print("🌍 Proxy List එක Download කරමින්...")
    all_proxies = set()
    for url in PROXY_SOURCES:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                lines = r.text.splitlines()
                for line in lines:
                    if line.strip() and ":" in line:
                        all_proxies.add(line.strip())
        except:
            continue
    print(f"✅ මුළු Proxies ගණන: {len(all_proxies)}")
    return list(all_proxies)

def check_proxy(proxy_ip):
    proxy_dict = {"http": f"http://{proxy_ip}", "https": f"http://{proxy_ip}"}
    try:
        start_time = time.time()
        r = requests.get(SPACE_URL, proxies=proxy_dict, timeout=PROXY_CHECK_TIMEOUT)
        
        latency = (time.time() - start_time) * 1000 
        
        if r.status_code == 200:
            return proxy_dict, latency
    except:
        return None

def get_working_proxy_fast(proxy_list):
    print(f"⚡ spped Proxy එකක් හොයමින් (Scanning {THREAD_COUNT} at a time)...")
    random.shuffle(proxy_list)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        batch_proxies = proxy_list[:300] # Batch size එකත් වැඩි කළා
        future_to_proxy = {executor.submit(check_proxy, p): p for p in batch_proxies}
        
        for future in concurrent.futures.as_completed(future_to_proxy):
            result = future.result()
            if result:
                proxy, latency = result
                print(f"🟢 Found Fast Proxy: {proxy['http']} (Ping: {latency:.0f}ms)")
                executor.shutdown(wait=False)
                return proxy
                
    print("❌ මේ Batch එකේ Fast Proxy එකක් නෑ. ඊළඟ Batch එක බලනවා...")
    return None


all_proxies = get_all_proxies()

while True:
    good_proxy = get_working_proxy_fast(all_proxies)
    
    if not good_proxy:
        time.sleep(1)
        continue

    try:
        session = requests.Session()
        session.proxies.update(good_proxy)
        
        # --- A. Upload ---
        print(f"📤 Uploading Image...")
        with open(IMAGE_PATH, 'rb') as f:
            files = {'files': f}
            upload_res = session.post(f"{SPACE_URL}/gradio_api/upload", files=files, timeout=15)
        
        if upload_res.status_code != 200:
            raise Exception(f"Upload Failed: {upload_res.status_code}")
            
        uploaded_path = upload_res.json()[0]
        
        # --- B. Queue ---
        print("🚀 Sending Job...")
        session_hash = str(uuid.uuid4())[:10]
        payload = {
            "data": [
                {"path": uploaded_path, "url": f"{SPACE_URL}/file={uploaded_path}", 
                 "orig_name": "img.jpg", "size": 0, "mime_type": "image/jpeg", "meta": {"_type": "gradio.FileData"}},
                "make this image come alive, cinematic motion, smooth animation", 
                6, "low quality, error", 3.5, 1, 1, 42, True
            ],
            "fn_index": 0, "session_hash": session_hash
        }
        
        session.post(f"{SPACE_URL}/gradio_api/queue/join", json=payload, timeout=15)
        
        # --- C. Listen ---
        print("⏳ Waiting for video...")
        stream_url = f"{SPACE_URL}/gradio_api/queue/data?session_hash={session_hash}"
        res = session.get(stream_url, stream=True, timeout=90)
        
        video_url = None
        for line in res.iter_lines():
            if line:
                decoded = line.decode('utf-8').replace('data: ', '')
                try:
                    data = json.loads(decoded)
                    if data.get('msg') == 'process_completed':
                        vid_data = data.get('output', {}).get('data', [])[0]
                        video_url = vid_data.get('url') or f"{SPACE_URL}/file={vid_data['path']}"
                        break
                except: pass
        
        if video_url:
            print(f"🎉 Success! URL Generated")
            print("⬇️ Downloading via Proxy (Same IP)...")
            
            r = session.get(video_url, stream=True, timeout=60)
            
            if r.status_code == 200:
                with open(OUTPUT_FILENAME, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024*1024): # 1MB chunks
                        f.write(chunk)
                print(f"✅ Download Complete: {OUTPUT_FILENAME}")
                break 
            else:
                raise Exception(f"Download Failed Status: {r.status_code}")

    except Exception as e:
        print(f"⚠️ Proxy Slow/Failed ({str(e)[:50]}...). Next proxy! ⏩")
