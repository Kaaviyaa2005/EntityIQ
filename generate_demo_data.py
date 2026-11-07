"""Create a reproducible 10,000-record synthetic benchmark with pair labels."""
from pathlib import Path
import random, pandas as pd
random.seed(42)
N_ENTITIES = 5000
VARIANTS = 2
names = ["Aster", "Blue Oak", "Cedar", "Delta", "Evergreen", "Fox", "Golden", "Harbor",
         "Indigo", "Juniper", "Keystone", "Lumen", "Metro", "Nova", "Orchid", "Pioneer"]
types = ["Foods", "Logistics", "Technologies", "Retail", "Services", "Industries"]
rows, truth = [], []
for i in range(N_ENTITIES):
    base = f"{random.choice(names)} {random.choice(names)} {random.choice(types)} Group {i:04d}"
    street = f"{random.randint(1,999)} {random.choice(['Main','Lake','Park','Market','Hill'])} Street"
    city = random.choice(["Madurai","Chennai","Coimbatore","Bengaluru","Hyderabad"])
    postal = str(random.randint(600001,699999))
    phone = "9" + "".join(random.choices("0123456789", k=9))
    domain = base.lower().replace(" ","") + ".com"
    for v in range(VARIANTS):
        name = base if v == 0 else base.replace("Technologies","Tech").replace("Services","Svc")
        address = street if v == 0 else street.replace("Street","St.")
        rows.append({"record_id":f"demo_{i}_{v}", "business_name":name, "address":address,
                     "phone":phone if random.random() > .08 else "",
                     "email":f"contact{i}@example.com" if random.random() > .15 else "",
                     "website":f"https://www.{domain}/" if random.random() > .10 else "",
                     "postal_code":postal, "city":city, "state":"Tamil Nadu", "country":"India",
                     "source":"directory_a" if v == 0 else "directory_b"})
    truth.append({"left_record_id":f"businesses_a_demo_{i}_0","right_record_id":f"businesses_b_demo_{i}_1"})
Path("data/raw").mkdir(parents=True, exist_ok=True)
pd.DataFrame([r for r in rows if r["record_id"].endswith("_0")]).to_csv("data/raw/businesses_a.csv", index=False)
pd.DataFrame([r for r in rows if r["record_id"].endswith("_1")]).to_csv("data/raw/businesses_b.csv", index=False)
pd.DataFrame(truth).to_csv("data/raw/ground_truth_pairs.csv", index=False)
print(f"Wrote {len(rows):,} records across {N_ENTITIES:,} entities.")
