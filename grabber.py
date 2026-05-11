import requests
import xml.etree.ElementTree as ET
import gzip
from datetime import datetime, timedelta
import os

# ==================== KONFIGURASI ====================
# 1. Daftar URL sumber EPG (bisa link .xml atau .xml.gz)
SOURCES = [
    "https://www.open-epg.com/files/indonesia.xml",
    "https://raw.githubusercontent.com/apistech/project/refs/heads/main/ApisTECH.xml",
    "https://www.open-epg.com/files/malaysia1.xml",
    "https://epg.pw/api/epg.xml?channel_id=400477",
    "https://epg.pw/api/epg.xml?channel_id=400480",
    "https://epg.pw/api/epg.xml?channel_id=400479",
    "https://epg.pw/api/epg.xml?channel_id=400478",
    "https://epg.pw/api/epg.xml?channel_id=524073",
    "https://www.open-epg.com/files/slovakia2.xml"
]
# 2. Daftar Channel ID yang ingin kamu ambil (sesuaikan dengan ID di sumber)
WANTED_CHANNELS = ["beinsports1.id", "beinsports2.id", "beinsports3.id", "beinsports4.id", "soccerchannel.id", "sportstars.id", "sportstars2.id", "sportstars3.id", "sportstars4.id", "Sport 1.sk", "Sport 2.sk", "spotv.id", "spotv2.id", "400477", "400480", "400479", "400478", "TVRISport.id@SD", "AnimaxAsia.sg@SD", "celestialmovies.id", "cinemax.id", "galaxy.id", "galaxypremium.id", "hbo.id", "hbofamily.id", "hbohits.id", "hbosignature.id", "imc.id", "tvnmovies.id", "antv.id", "CNBCIndonesia.id@SD", "CNNIndonesia.id@SD", "DiscoveryChannelSoutheastAsia.sg@SD", "GTV.id@SD", "indosiar.id", "inews.id", "jaktv.id", "kompastv.id", "mdtv.id", "mnctv.id", "moji.id", "rcti.id", "rtv.id", "sindonewstv.id", "sctv.id", "Trans7.id", "TransTV.id", "tvone.id", "tvri.id", "Okey.my", "Sukan RTM.my"]

# 3. Header agar dianggap browser asli
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}
# =====================================================

def convert_to_plus_7(time_str):
    """Mengonversi format waktu XMLTV ke UTC+7 (WIB)"""
    if not time_str:
        return time_str
    try:
        # Format XMLTV biasanya: 20260512000000 +0000
        parts = time_str.split(" ")
        clean_time = parts[0]
        
        # Parse waktu dasar
        dt = datetime.strptime(clean_time[:14], "%Y%m%d%H%M%S")
        
        # Ambil offset asal (misal +0000, +0200, atau -0500)
        if len(parts) > 1:
            offset_str = parts[1]
            offset_hours = int(offset_str[:3])
            offset_mins = int(offset_str[0] + offset_str[3:])
            # Normalkan ke UTC dulu
            dt = dt - timedelta(hours=offset_hours, minutes=offset_mins)
        
        # Tambahkan 7 jam untuk WIB
        dt_wib = dt + timedelta(hours=7)
        return dt_wib.strftime("%Y%m%d%H%M%S") + " +0700"
    except Exception as e:
        print(f"⚠️ Gagal konversi waktu {time_str}: {e}")
        return time_str

def create_epg():
    # Inisialisasi Root XMLTV Baru
    new_root = ET.Element("tv")
    new_root.set("generator-info-name", "Rakuda-EPG-Aggregator")
    
    channels_added = set()
    program_count = 0

    for url in SOURCES:
        try:
            print(f"📡 Menghubungi: {url}...")
            response = requests.get(url, headers=HEADERS, timeout=60)
            
            if response.status_code != 200:
                print(f"❌ Error {response.status_code} pada {url}")
                continue

            content = response.content

            # Cek jika file terkompresi Gzip
            if url.endswith('.gz') or content.startswith(b'\x1f\x8b'):
                print(f"📦 Mengekstrak Gzip...")
                content = gzip.decompress(content)

            # Parse XML
            root = ET.fromstring(content)
            print(f"✅ XML Berhasil dimuat.")

            # 1. Filter & Tambah Elemen <channel>
            for channel in root.findall("channel"):
                ch_id = channel.get("id")
                if ch_id in WANTED_CHANNELS and ch_id not in channels_added:
                    new_root.append(channel)
                    channels_added.add(ch_id)

            # 2. Filter & Tambah Elemen <programme>
            for programme in root.findall("programme"):
                ch_id = programme.get("channel")
                if ch_id in WANTED_CHANNELS:
                    # Ambil dan konversi waktu start/stop
                    start = programme.get("start")
                    stop = programme.get("stop")
                    
                    programme.set("start", convert_to_plus_7(start))
                    programme.set("stop", convert_to_plus_7(stop))
                    
                    new_root.append(programme)
                    program_count += 1

        except Exception as e:
            print(f"❌ Gagal memproses {url}: {e}")

    # Simpan file akhir
    print(f"📝 Menyusun file akhir dengan {len(channels_added)} channel dan {program_count} jadwal...")
    tree = ET.ElementTree(new_root)
    
    # Simpan ke folder yang sama dengan script
    output_file = "my_epg.xml"
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    
    # Cek ukuran file
    file_size = os.path.getsize(output_file) / 1024
    print(f"🚀 Selesai! File: {output_file} ({file_size:.2f} KB)")

if __name__ == "__main__":
    create_epg()
