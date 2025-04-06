import streamlit as st
import os
import json
from datetime import datetime
from PIL import Image
import uuid

st.set_page_config(page_title="E-Lapor Mas Rizxy", layout="centered")

#Folder dan File
DATA_FOLDER = "data"
IMAGE_FOLDER = os.path.join(DATA_FOLDER, "images")
JSON_FILE = os.path.join(DATA_FOLDER, "laporan.json")
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

#Fungsi untuk baca data
def load_data():
    if os.path.exists(JSON_FILE) and os.path.getsize(JSON_FILE) > 0:
        with open(JSON_FILE, "r") as file:
            return json.load(file)
    return []

#fungsi untuk simpan data
def save_data(data):
    with open(JSON_FILE, "w") as file:
        json.dump(data, file, indent=2)

#sidebar navigasi
page = st.sidebar.selectbox("Pilih halaman", ["Kirim Laporan", "Laporan Masuk"])

if page == "Kirim Laporan":
    st.title("📮 E-Lapor Mas Rizxy")
    st.subheader("Kirim laporan dari daerahmu!")

    nama = st.text_input("Nama")
    lokasi = st.text_input("Lokasi Kejadian")
    laporan = st.text_area("Isi laporan")
    gambar = st.file_uploader("Upload Gambar Bukti (Opsional)", type=["jpg, jpeg, png"])

    if st.button("Kirim Laporan"):
        if nama and lokasi and laporan:
            image_filename = None

            #simpan gambar jika ada
            if gambar:
                image_id = str(uuid.uuid4())
                ext = os.path.split('.')[-1]
                image_filename = f"{image_id}.{ext}"
                image_path = os.path.join(IMAGE_FOLDER, image_filename)
                with open(image_path, "wb") as f:
                    f.write(gambar.getbuffer())

            new_entry = {
                "nama": nama,
                "lokasi": lokasi,
                "laporan": laporan,
                "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "gambar": image_filename
            }

            data = load_data()
            data.append(new_entry)
            save_data(data)
            st.success("Laporan berhasil dikirim!")
        else:
            st.warning("Nama, lokasi dan isi laporan harus diisi.")

elif page =="Laporan Masuk":
    st.title("📋Laporan Masuk")

    data = load_data()
    if data:
        for i, laporan in enumerate(data[::-1], 1): #terbaru dulu
            st.markdown(f"### 📋 Laporan #{i}")
            st.write(f"**Nama:** {laporan['nama']}")
            st.write(f"**Lokasi:** {laporan['lokasi']}")
            st.write(f"**Laporan:** {laporan['laporan']}")
            st.write(f"🕒 **Waktu:** {laporan['waktu']}")

            #tampilkan gambar jika ada
            if laporan.get("gambar"):
                image_path = os.path.join(IMAGE_FOLDER, laporan["gambar"])
                if os.path.exists(image_path):
                    st.image(image_path, width=400, caption="Bukti Foto")

            st.markdown("---")
    else:
        st.info("Belum ada laporan masuk.")
