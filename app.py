import os
import pandas as pd
from dotenv import load_dotenv
from llama_cpp import Llama

# Load .env
load_dotenv()
model_path = os.getenv("MODEL_PATH")

# Load model
print("🔁 Memuat model...")
llm = Llama(
    model_path=model_path, n_ctx=1024, n_threads=4, n_gpu_layers=0, verbose=False
)
print("✅ Model berhasil dimuat!")

# Load data Excel
df = pd.read_excel("data/sales.xlsx", sheet_name="data")
df["Date"] = pd.to_datetime(df["Date"])
context_data = df.to_markdown(index=False)

print("\n=== 🤖 Asisten Penjualan AI (Lokal, Bahasa Indonesia) ===")
print("Tanya apa saja tentang data penjualan. Ketik 'exit' untuk keluar.\n")


def jawab_dengan_pandas(question: str) -> str | None:
    q = question.lower()

    # Total seluruh sales
    if "semua sales" in q or "total sales" in q or "total penjualan" in q:
        total = df["Sales"].sum()
        return f"Total seluruh penjualan adalah {total}."

    # Produk tertentu
    if "product" in q or "produk" in q:
        for p in df["Product"].unique():
            if p.lower() in q:
                total = df[df["Product"].str.lower() == p.lower()]["Sales"].sum()
                return f"Berdasarkan data penjualan, total penjualan untuk produk {p} adalah {total}."

    # Kota
    for city in df["kota"].unique():
        if city.lower() in q:
            total = df[df["kota"].str.lower() == city.lower()]["Sales"].sum()
            return f"Total penjualan di {city} adalah {total}."

    # Bulan
    bulan_dict = {
        "januari": 1,
        "februari": 2,
        "maret": 3,
        "april": 4,
        "mei": 5,
        "juni": 6,
        "juli": 7,
        "agustus": 8,
        "september": 9,
        "oktober": 10,
        "november": 11,
        "desember": 12,
    }
    for nama_bulan, nomor_bulan in bulan_dict.items():
        if nama_bulan in q:
            total = df[df["Date"].dt.month == nomor_bulan]["Sales"].sum()
            return (
                f"Total penjualan pada bulan {nama_bulan.capitalize()} adalah {total}."
            )

    return None


# Loop interaktif
while True:
    question = input("❓ Pertanyaan: ")
    if question.lower() in ["exit", "quit"]:
        print("👋 Terima kasih! Sesi selesai.")
        break

    jawaban_pandas = jawab_dengan_pandas(question)

    # ✅ Langsung tampilkan jawaban jika bisa dijawab tanpa LLM
    if jawaban_pandas:
        print(f"🤖 Jawaban: {jawaban_pandas}\n")
        continue

    # 🔁 Gunakan LLM jika jawaban belum tersedia
    prompt = f"""
Kamu adalah analis data penjualan. Data berikut ini disajikan dalam bentuk tabel markdown:

{context_data}

Pengguna bertanya: "{question}"

Jawab dalam Bahasa Indonesia yang sopan dan profesional.
"""

    try:
        response = llm(prompt, max_tokens=256, stop=["Pengguna:", "Asisten:"])
        answer = response["choices"][0]["text"].strip()
        print(f"🤖 Jawaban: {answer}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
