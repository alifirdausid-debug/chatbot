import streamlit as st
import fitz  # PyMuPDF
from openai import OpenAI
import io

# --- FUNGSI UNTUK EKSTRAKSI TEKS DARI PDF ---
def extract_text_from_pdf(pdf_file):
    """
    Mengekstrak teks dari file PDF yang diunggah.
    Menggunakan PyMuPDF (fitz) untuk membaca teks dari setiap halaman.
    """
    try:
        # Membuka PDF dari byte stream di memori
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        full_text = ""
        # Melakukan iterasi pada setiap halaman untuk mengekstrak teks
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            full_text += page.get_text()
        pdf_document.close()
        return full_text
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file PDF: {e}")
        return None

# --- FUNGSI UNTUK ANALISIS KONTRAK MENGGUNAKAN OPENAI ---
def analyze_contract(api_key, contract_text):
    """
    Mengirim teks kontrak ke OpenAI API untuk dianalisis.
    Prompt dirancang untuk mengekstrak informasi kunci dari kontrak.
    """
    try:
        client = OpenAI(api_key=api_key)
        
        # Prompt yang dirancang khusus untuk analisis kontrak
        prompt_template = f"""
        Anda adalah seorang asisten legal AI yang sangat teliti dan ahli dalam menganalisis dokumen hukum.
        Tugas Anda adalah untuk menganalisis teks kontrak berikut dan memberikan ringkasan yang jelas dan terstruktur.

        Tolong identifikasi dan jelaskan poin-poin berikut dari teks kontrak di bawah ini:

        1.  **Para Pihak yang Terlibat**: Identifikasi semua pihak yang disebutkan dalam kontrak beserta peran mereka.
        2.  **Ringkasan Eksekutif**: Berikan ringkasan singkat (2-3 kalimat) mengenai tujuan utama dari kontrak ini.
        3.  **Klausul-Klausul Penting**:
            *   **Kewajiban Utama**: Apa saja kewajiban utama dari masing-masing pihak?
            *   **Jangka Waktu**: Kapan kontrak ini dimulai, berakhir, dan apa saja ketentuan perpanjangannya?
            *   **Ketentuan Pembayaran**: Bagaimana, kapan, dan berapa jumlah pembayaran yang harus dilakukan?
            *   **Kerahasiaan (Confidentiality)**: Apakah ada klausul kerahasiaan? Jika ya, jelaskan secara singkat.
            *   **Penyelesaian Sengketa (Dispute Resolution)**: Bagaimana sengketa akan diselesaikan menurut kontrak ini (mediasi, arbitrase, pengadilan)?
            *   **Pengakhiran Kontrak (Termination)**: Apa saja kondisi yang memungkinkan salah satu pihak untuk mengakhiri kontrak?
        4.  **Potensi Risiko atau Area Abu-abu**: Identifikasi klausul yang mungkin ambigu, tidak biasa, atau berpotensi merugikan salah satu pihak. Berikan saran singkat jika ada.

        Gunakan format Markdown untuk jawaban yang rapi.

        --- TEKS KONTRAK ---
        {contract_text}
        --- AKHIR TEKS KONTRAK ---
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Anda adalah asisten legal AI."},
                {"role": "user", "content": prompt_template}
            ],
            temperature=0.2, # Mengurangi kreativitas untuk jawaban yang lebih faktual
        )
        return response.choices[0].message.content

    except Exception as e:
        st.error(f"Terjadi kesalahan saat menghubungi OpenAI API: {e}")
        return None

# --- UI STREAMLIT ---
st.title("📄 Analisis Dokumen Kontrak dengan AI")
st.markdown("Unggah dokumen kontrak dalam format PDF untuk dianalisis oleh AI. Masukkan API key OpenAI Anda di sidebar.")

# Sidebar untuk input API Key
with st.sidebar:
    st.header("Pengaturan")
    openai_api_key = st.text_input("Masukkan OpenAI API Key Anda", type="password", help="Dapatkan API key Anda dari platform OpenAI.")
    st.markdown("[Dapatkan OpenAI API Key](https://platform.openai.com/account/api-keys)")

# Komponen untuk mengunggah file
uploaded_file = st.file_uploader("Pilih file PDF kontrak Anda", type="pdf")

# Tombol untuk memulai analisis
if st.button("Analisa Dokumen"):
    if uploaded_file is not None:
        if openai_api_key:
            with st.spinner('Sedang menganalisa dokumen... Proses ini mungkin memakan waktu beberapa saat.'):
                # 1. Ekstrak teks dari PDF
                extracted_text = extract_text_from_pdf(uploaded_file)
                
                if extracted_text:
                    st.info("Ekstraksi teks dari PDF berhasil. Mengirim ke OpenAI untuk dianalisis...")
                    # 2. Analisis teks dengan OpenAI
                    analysis_result = analyze_contract(openai_api_key, extracted_text)
                    
                    if analysis_result:
                        # 3. Tampilkan hasil analisis
                        st.subheader("Hasil Analisis Kontrak")
                        st.markdown(analysis_result)
        else:
            st.warning("Mohon masukkan OpenAI API Key Anda di sidebar untuk melanjutkan.")
    else:
        st.warning("Mohon unggah file PDF kontrak Anda terlebih dahulu.")

st.sidebar.info(
    "Aplikasi ini menggunakan model bahasa dari OpenAI untuk menganalisis dokumen. "
    "Hasil analisis bersifat informatif dan bukan merupakan nasihat hukum."
)
