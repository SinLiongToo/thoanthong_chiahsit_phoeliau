import os
import sys
import time
import urllib.request

# Reconfigure stdout to use UTF-8 to prevent encoding errors on Windows cp950 consoles
sys.stdout.reconfigure(encoding='utf-8')

# Mapping of audio IDs to their corresponding Taiwanese terms/roles for logging purposes
audio_ids_map = {
    # Verbs / Grammar / Particles
    "07923": "這 (tse)",
    "05013": "是 (sī)",
    "03153": "我 (guá)",
    "04386": "的 (ê - 關係詞)",
    "02449": "有 (ū)",
    "00674": "內底 (lāi-té)",
    "10940": "閣 (koh)",
    "50009": "已經 (í-king)",
    "02282": "好 (hó)",
    "03350": "矣 (ah)",
    "06396": "真 (tsin)",
    "04443": "芳 (phang)",
    "21044": "貢 (kòng - 芳貢貢的貢)",
    "08197": "喔 (o)",
    "07093": "啦 (la)",
    "10785": "緊 (kín)",
    "03543": "來 (lâi)",
    "05588": "食 (tsiah)",
    "07493": "欲 (beh)",
    "09691": "準備 (tsún-pī)",
    "00573": "予 (hōo)",
    "00596": "勻 (ûn)",
    "10084": "誠 (tsiânn)",
    "07042": "啉 (lim - 喝)",
    "07530": "淋 (lâm)",
    "07688": "甜粅粅 (tinn-but-but)",

    # Modes & actions
    "02788": "肉粽 (bah-tsàng)",
    "11864": "縛 (pa̍k)",
    "13026": "礤冰 (tshuah-ping)",
    "13020": "礤 (tshuah - 動詞)",
    "11235": "潤餅 (lūn-piánn)",
    "01394": "包 (pau - 動詞)",
    "06422": "真珠 (tsin-tsu - 珍珠)",
    "53466": "奶茶 (nî-tê)",
    "09505": "搖 (iô)",
    "06248": "烏 (oo - 黑輪的烏)",
    "11511": "輪 (liân - 黑輪的輪)",
    "11809": "燙 (thng)",

    # Numbers & unit
    "00001": "一 (tsi̍t)",
    "03597": "兩 (nnḡ)",
    "00170": "三 (sann)",
    "01418": "四 (sì)",
    "00574": "五 (gōo)",
    "00587": "六 (la̍k)",
    "00047": "七 (tshit)",
    "00055": "八 (pueh)",
    "00048": "九 (káu)",
    "00061": "十 (tsa̍p)",
    "00179": "个 (ê - 量詞)",

    # Ingredients
    "02987": "卵仁 (yolk)",
    "05658": "香菇 (mushroom)",
    "09404": "土豆 (peanut - 塗豆)",
    "10613": "滷肉 (pork)",
    "06116": "栗子 (chestnut)",
    "11369": "蝦米 (shrimp)",
    "13083": "魷魚 (squid - 鰇魚)",
    "13087": "鹹 (salted)",
    "12135": "鴨卵 (duck egg - 鹹蛋的蛋)",
    "53611": "紅豆 (redbean)",
    "10745": "綠豆仔 (mungbean)",
    "06478": "粉圓 (pearl)",
    "03492": "芋圓 (taroball)",
    "12372": "愛玉 (aiyu - 薁蕘)",
    "01362": "仙草 (grassjelly)",
    "06487": "粉粿 (pinkkui)",
    "01238": "牛奶 (milk - 煉乳的奶)",
    "10814": "膏 (paste - 煉乳的膏)",
    "06451": "粉 (powder - 花生粉的粉)",
    "11879": "糖粉 (sugar)",
    "06926": "高麗菜 (cabbage)",
    "03486": "豆菜 (bean sprouts - 豆芽菜)",
    "05454": "紅糟 (redpork)",
    "03470": "豆乾 (tofu)",
    "09717": "煎 (panfry - 煎蛋絲 the 煎)",
    "02967": "卵 (egg - 煎蛋絲 the 蛋)",
    "08860": "絲 (shreds - 煎蛋絲 the 絲)",
    "04477": "芫荽 (coriander - 香菜)",
    "09605": "椰子 (coconut - 椰果)",
    "01652": "布 (cotton - 布丁 the 布)",
    "00046": "丁 (t-shape - 布丁 the 丁)",
    "02113": "冰 (ice)",
    "10729": "綠 (green - 綠茶凍 the 綠)",
    "06559": "茶 (tea - 綠茶凍 the 茶)",
    "05738": "凍 (jelly - 綠茶凍 the 凍)",
    "08325": "寒天 (kanten)",
    "03448": "芋泥 (taropaste)",
    "00792": "天 (heaven - 甜不辣 the 天)",
    "07159": "婦 (woman - 甜不辣 the 婦)",
    "22743": "羅 (net - 甜不辣 the 羅)",
    "02599": "米 (rice - 米血 the 米)",
    "02615": "血 (blood - 米血 the 血)",
    "07655": "甜 (sweet - 甜辣醬 the 甜)",
    "10888": "辣 (chili - 甜辣醬 the 辣)",
    "12686": "醬 (sauce - 甜辣醬 the 醬)",
    "08996": "菜頭 (radish)",
    "06707": "貢丸 (porkball)",
    "08115": "魚丸 (fishball)",
    "03504": "豆腐 (fried-tofu - 油豆腐)"
}

cdn_base = "https://1763c5ee9859e0316ed6-db85b55a6a3fbe33f09b9245992383bd.ssl.cf1.rackcdn.com"

def download_audio_files():
    # Ensure audio directory exists
    os.makedirs("audio", exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    total = len(audio_ids_map)
    print(f"開始自萌典台語 CDN 下載語音檔 (共 {total} 個)...")
    
    success_count = 0
    skip_count = 0
    failed_count = 0
    
    for i, (audio_id, name) in enumerate(audio_ids_map.items(), 1):
        filename = f"{audio_id}.ogg"
        target_path = os.path.join("audio", filename)
        
        if os.path.exists(target_path):
            print(f"[{i}/{total}] 已存在，跳過: {filename} ({name})")
            skip_count += 1
            success_count += 1
            continue
            
        url = f"{cdn_base}/{filename}"
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read()
                # Double check that we didn't receive HTML (fake success page)
                if b"<!doctype html>" in content.lower() or b"<html" in content.lower():
                    print(f"[{i}/{total}] 下載失敗: {filename} ({name}) - 伺服器返回了 HTML 網頁而非音檔")
                    failed_count += 1
                else:
                    with open(target_path, "wb") as f:
                        f.write(content)
                    print(f"[{i}/{total}] 下載成功: {filename} -> {name} (大小: {len(content)} 位元組)")
                    success_count += 1
        except Exception as e:
            print(f"[{i}/{total}] 下載失敗: {filename} ({name}) - 錯誤: {e}")
            failed_count += 1
            
        # Pacing
        time.sleep(0.2)
        
    print(f"\n所有下載程序結束！")
    print(f"總計 {total} 個音檔：成功 (含已存在) {success_count} 個，跳過 {skip_count} 個，失敗 {failed_count} 個。")
    print("請確認 audio/ 資料夾下的音檔。")

if __name__ == "__main__":
    download_audio_files()
