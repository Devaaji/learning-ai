import os
import pandas as pd # type: ignore
from dotenv import load_dotenv # type: ignore
from llama_cpp import Llama # type: ignore

# Load .env
load_dotenv()
model_path = os.getenv("MODEL_PATH")

# Load model
print("🔁 Loading model...")
llm = Llama(
    model_path=model_path,
    n_ctx=1024,
    n_threads=4,         # Boleh disesuaikan
    n_gpu_layers=20,     # Untuk Mac M1 (jika kamu pakai metal build)
    verbose=False
)
print("✅ Model loaded!")

# Load Excel
df = pd.read_excel("data/sales.xlsx", sheet_name="data")

# Ambil 5 baris awal sebagai konteks
context_data = df.head(5).to_markdown()

# Prompt dasar
BASE_PROMPT = f"""
You are a data analyst. Based on the following sales data (in markdown table format), answer user questions accurately.

Sales data:
{context_data}

"""

# CLI interaktif
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
