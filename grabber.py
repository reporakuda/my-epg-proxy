import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# Konfigurasi
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

WANTED_CHANNELS = ["beinsports1.id", "beinsports2.id", "beinsports3.id", "beinsports4.id", "soccerchannel.id", "sportstars.id", "sportstars2.id", "sportstars3.id", "sportstars4.id", "Sport 1.sk", "Sport 2.sk", "spotv.id", "spotv2.id", "400477", "400480", "400479", "400478", "TVRISport.id@SD", "AnimaxAsia.sg@SD", "celestialmovies.id", "cinemax.id", "galaxy.id", "galaxypremium.id", "hbo.id", "hbofamily.id", "hbohits.id", "hbosignature.id", "imc.id", "tvnmovies.id", "antv.id", "CNBCIndonesia.id@SD", "CNNIndonesia.id@SD", "DiscoveryChannelSoutheastAsia.sg@SD", "GTV.id@SD", "indosiar.id", "inews.id", "jaktv.id", "kompastv.id", "mdtv.id", "mnctv.id", "moji.id", "rcti.id", "rtv.id", "sindonewstv.id", "sctv.id", "Trans7.id", "TransTV.id", "tvone.id", "tvri.id", "Okey.my", "Sukan RTM.my"]

def convert_to_plus_7(time_str):
    """Mengubah format waktu EPG apa pun menjadi +0700"""
    try:
        # Format XMLTV: 20260512000000 +0000
        # Kita ambil 14 angka pertama (YYYYMMDDHHMMSS) dan offset-nya
        clean_time = time_str.split(" ")[0]
        offset_str = time_str.split(" ")[1]

        # Ubah string ke objek datetime
        dt = datetime.strptime(clean_time, "%Y%m%d%H%M%S")

        # Ambil angka offset (misal +0000 atau +0200)
        offset_hours = int(offset_str[:3]) 
        
        # 1. Normalkan dulu ke UTC (+0)
        dt_utc = dt - timedelta(hours=offset_hours)
        
        # 2. Tambahkan 7 jam untuk menjadi WIB (+7)
        dt_wib = dt_utc + timedelta(hours=7)

        # Kembalikan ke format XMLTV dengan akhiran +0700
        return dt_wib.strftime("%Y%m%d%H%M%S") + " +0700"
    except:
        return time_str # Jika gagal, balikin waktu asli

def create_epg():
    new_root = ET.Element("tv")
    new_root.set("generator-info-name", "Rakuda EPG Custom")

    channels_added = []

    for url in SOURCES:
        try:
            print(f"📡 Mengunduh: {url}")
            response = requests.get(url, timeout=30)
            root = ET.fromstring(response.content)

            # 1. Ambil Channel Info
            for channel in root.findall("channel"):
                ch_id = channel.get("id")
                if ch_id in WANTED_CHANNELS and ch_id not in channels_added:
                    new_root.append(channel)
                    channels_added.append(ch_id)

            # 2. Ambil Program & Sesuaikan Timezone
            for programme in root.findall("programme"):
                ch_id = programme.get("channel")
                if ch_id in WANTED_CHANNELS:
                    # Ambil waktu start & stop
                    start = programme.get("start")
                    stop = programme.get("stop")

                    # Konversi ke +0700
                    if start:
                        programme.set("start", convert_to_plus_7(start))
                    if stop:
                        programme.set("stop", convert_to_plus_7(stop))
                    
                    new_root.append(programme)

        except Exception as e:
            print(f"❌ Error di {url}: {e}")

    # Simpan
    tree = ET.ElementTree(new_root)
    tree.write("my_epg.xml", encoding="utf-8", xml_declaration=True)
    print("✅ Beres! Semua waktu sudah dikonversi ke +0700 (WIB).")

if __name__ == "__main__":
    create_epg()
