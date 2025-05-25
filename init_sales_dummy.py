import os
import random
import psycopg2
from faker import Faker
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
fake = Faker("id_ID")

# Koneksi database
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=os.getenv("DB_PORT", 8510),
    database=os.getenv("DB_NAME", "training-ai"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASS", "0000")
)
cur = conn.cursor()

# 1. Buat tabel jika belum ada
cur.execute("""
CREATE TABLE IF NOT EXISTS sales_data (
    id SERIAL PRIMARY KEY,
    date DATE,
    city VARCHAR(100),
    product VARCHAR(100),
    sales INTEGER,
    sales_person VARCHAR(100)
)
""")

# 2. Data dummy
cities = ["Jakarta", "Bandung", "Surabaya", "Medan", "Yogyakarta"]
products = ["A", "B", "C", "D", "E"]

data = []
for _ in range(100):
    date = fake.date_between(start_date="-90d", end_date="today")
    city = random.choice(cities)
    product = random.choice(products)
    sales = random.randint(50, 500)
    sales_person = fake.name()
    data.append((date, city, product, sales, sales_person))

# 3. Insert data
cur.executemany("""
    INSERT INTO sales_data (date, city, product, sales, sales_person)
    VALUES (%s, %s, %s, %s, %s)
""", data)

conn.commit()
cur.close()
conn.close()

print("✅ Data dummy berhasil dimasukkan ke tabel sales_data.")

# import psycopg2
# from random import choice, randint
# from datetime import datetime, timedelta

# # Koneksi ke PostgreSQL
# conn = psycopg2.connect(
#     dbname="training-ai",  # ganti sesuai nama database kamu
#     user="postgres",
#     password="0000",  # ganti sesuai password kamu
#     host="127.0.0.1",
#     port="8510",
# )
# cur = conn.cursor()

# # Data acuan
# cities = ["Jakarta", "Bandung", "Surabaya", "Medan", "Semarang"]
# products = ["A", "B", "C", "D", "E"]
# sales_names = [
#     "Andi",
#     "Budi",
#     "Citra",
#     "Dewi",
#     "Eka",
#     "Fajar",
#     "Gita",
#     "Hadi",
#     "Indra",
#     "Joko",
# ]

# # Buat 100 baris dummy data
# dummy_data = []
# start_date = datetime(2024, 5, 1)

# for _ in range(100):
#     date = (start_date + timedelta(days=randint(0, 90))).date()
#     city = choice(cities)
#     product = choice(products)
#     sales = randint(50, 300)
#     sales_name = choice(sales_names)
#     dummy_data.append((date, city, product, sales, sales_name))

# # Insert ke database
# cur.executemany(
#     """
#     INSERT INTO sales_data (date, city, product, sales, sales_name)
#     VALUES (%s, %s, %s, %s, %s)
# """,
#     dummy_data,
# )

# conn.commit()
# cur.close()
# conn.close()
# print("✅ Dummy data berhasil dimasukkan ke database.")
