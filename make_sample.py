"""動作確認用: sample_data/<製作日>/ に複数部位入りのダミーSTLを生成する。"""
import os
import random
from datetime import date, timedelta

for day in range(10):
    d = date.today() - timedelta(days=day)
    folder = os.path.join("sample_data", d.strftime("%Y%m%d"))
    os.makedirs(folder, exist_ok=True)
    for i in range(6):
        due = d + timedelta(days=random.randint(3, 10))
        name = (f"{due:%Y%m%d}_{random.choice(['Zir', 'CAD', 'PMMA'])}_{random.choice(['A1', 'A2', 'B2'])}_"
                f"{random.choice([12345, 23456]):05d}_{i + 1:03d}_{random.choice(['14', '16-17', '36', '45-46-47'])}.stl")
        with open(os.path.join(folder, name), "wb") as f:
            f.write(b"solid test\nendsolid test\n")
open(os.path.join("sample_data", d.strftime("%Y%m%d"), "bad_name.stl"), "wb").close()
