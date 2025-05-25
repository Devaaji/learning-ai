import os
import time
import psycopg2 # type: ignore
from fastapi import FastAPI # type: ignore
from fastapi.responses import StreamingResponse # type: ignore
from pydantic import BaseModel # type: ignore
from llama_cpp import Llama # type: ignore
from dotenv import load_dotenv # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ubah jadi asal frontend kamu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
print("🔁 Loading model...")
llm = Llama(
    model_path=os.getenv("MODEL_PATH"), n_ctx=1024, n_threads=4, n_gpu_layers=20
)
print("✅ Model loaded!")


# DB connection
def get_sales_data():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT date, city, product, sales, sales_person FROM sales_data ORDER BY date DESC LIMIT 10"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def to_markdown(rows):
    header = "| Tanggal    | Kota    | Produk | Penjualan | Sales Person        |\n"
    header += "|------------|---------|--------|-----------|---------------------|\n"
    lines = []
    for r in rows:
        lines.append(f"| {r[0]} | {r[1]:<7} | {r[2]:<6} | {r[3]:<9} | {r[4]:<19} |")
    return header + "\n".join(lines)


class PromptRequest(BaseModel):
    prompt: str


@app.post("/stream")
def stream_response(request: PromptRequest):
    rows = get_sales_data()
    context_data = to_markdown(rows)

    full_prompt = f"""
Kamu adalah asisten data penjualan yang membantu menjawab pertanyaan berdasarkan data berikut ini:

{context_data}

Jawab dengan jelas dan singkat dalam bahasa Indonesia.
User: {request.prompt}
Assistant:"""

    def generate():
        for chunk in llm(
            full_prompt, max_tokens=512, stream=True, stop=["User:", "Assistant:"]
        ):
            token = chunk["choices"][0]["text"]
            yield token
            time.sleep(0.02)  # agar terasa seperti sedang mengetik

    return StreamingResponse(generate(), media_type="text/plain")


# import os
# import psycopg2
# from dotenv import load_dotenv
# from llama_cpp import Llama

# # Load env variables
# load_dotenv()
# model_path = os.getenv("MODEL_PATH")

# # Connect ke PostgreSQL
# conn = psycopg2.connect(
#     host=os.getenv("DB_HOST", "127.0.0.1"),
#     port=os.getenv("DB_PORT", 8510),
#     database=os.getenv("DB_NAME", "training-ai"),
#     user=os.getenv("DB_USER", "postgres"),
#     password=os.getenv("DB_PASS", "0000"),
# )
# cur = conn.cursor()

# # Ambil data sales contoh (misal 10 baris)
# cur.execute(
#     "SELECT date, city, product, sales, sales_person FROM sales_data ORDER BY date DESC LIMIT 10"
# )
# rows = cur.fetchall()


# # Format data jadi tabel markdown supaya AI paham
# def to_markdown(rows):
#     header = "| Tanggal    | Kota    | Produk | Penjualan | Sales Person        |\n"
#     header += "|------------|---------|--------|-----------|---------------------|\n"
#     lines = []
#     for r in rows:
#         lines.append(f"| {r[0]} | {r[1]:<7} | {r[2]:<6} | {r[3]:<9} | {r[4]:<19} |")
#     return header + "\n".join(lines)


# context_data = to_markdown(rows)

# # Load model LLaMA lokal
# print("🔁 Loading model...")
# llm = Llama(
#     model_path=model_path, n_ctx=1024, n_threads=4, n_gpu_layers=20, verbose=False
# )
# print("✅ Model loaded!")

# # Prompt dasar dalam bahasa Indonesia
# BASE_PROMPT = f"""
# Kamu adalah asisten data penjualan yang membantu menjawab pertanyaan berdasarkan data berikut ini:

# {context_data}

# Jawab dengan jelas dan singkat dalam bahasa Indonesia.
# """

# print("\n=== 🤖 AI Sales Assistant (Local LLaMA) ===")
# print("Tanya apa saja tentang data penjualan. Ketik 'exit' untuk keluar.\n")

# while True:
#     question = input("❓ Pertanyaan: ")
#     if question.lower() in ["exit", "quit"]:
#         print("👋 Terima kasih! Sesi selesai.")
#         break

#     full_prompt = BASE_PROMPT + "\nUser: " + question + "\nAssistant:"
#     try:
#         response = llm(full_prompt, max_tokens=512, stop=["User:", "Assistant:"])
#         answer = response["choices"][0]["text"].strip()
#         print(f"🤖 Jawaban: {answer}\n")
#     except Exception as e:
#         print(f"❌ Error: {e}\n")

# cur.close()
# conn.close()
