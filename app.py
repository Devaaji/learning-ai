import os
import psycopg2
from dotenv import load_dotenv
from llama_cpp import Llama

# Load env variables
load_dotenv()
model_path = os.getenv("MODEL_PATH")

# Connect ke PostgreSQL
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=os.getenv("DB_PORT", 8510),
    database=os.getenv("DB_NAME", "training-ai"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASS", "0000"),
)
cur = conn.cursor()

# Ambil data sales contoh (misal 10 baris)
cur.execute(
    "SELECT date, city, product, sales, sales_person FROM sales_data ORDER BY date DESC LIMIT 10"
)
rows = cur.fetchall()


# Format data jadi tabel markdown supaya AI paham
def to_markdown(rows):
    header = "| Tanggal    | Kota    | Produk | Penjualan | Sales Person        |\n"
    header += "|------------|---------|--------|-----------|---------------------|\n"
    lines = []
    for r in rows:
        lines.append(f"| {r[0]} | {r[1]:<7} | {r[2]:<6} | {r[3]:<9} | {r[4]:<19} |")
    return header + "\n".join(lines)


context_data = to_markdown(rows)

# Load model LLaMA lokal
print("🔁 Loading model...")
llm = Llama(
    model_path=model_path, n_ctx=1024, n_threads=4, n_gpu_layers=20, verbose=False
)
print("✅ Model loaded!")

# Prompt dasar dalam bahasa Indonesia
BASE_PROMPT = f"""
Kamu adalah asisten data penjualan yang membantu menjawab pertanyaan berdasarkan data berikut ini:

{context_data}

Jawab dengan jelas dan singkat dalam bahasa Indonesia.
"""

print("\n=== 🤖 AI Sales Assistant (Local LLaMA) ===")
print("Tanya apa saja tentang data penjualan. Ketik 'exit' untuk keluar.\n")

while True:
    question = input("❓ Pertanyaan: ")
    if question.lower() in ["exit", "quit"]:
        print("👋 Terima kasih! Sesi selesai.")
        break

    full_prompt = BASE_PROMPT + "\nUser: " + question + "\nAssistant:"
    try:
        response = llm(full_prompt, max_tokens=512, stop=["User:", "Assistant:"])
        answer = response["choices"][0]["text"].strip()
        print(f"🤖 Jawaban: {answer}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

cur.close()
conn.close()
