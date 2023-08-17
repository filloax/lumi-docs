import json
import os

DATA_DIR = "data/parsed"

all_data = []

for file in os.listdir(DATA_DIR):
    path = os.path.join(DATA_DIR, file)
    print(path)

    # Load the JSON data from the file
    with open(path, 'r') as json_file:
        data: list = json.load(json_file)
        all_data.extend(data)

all_data.sort(key=lambda e: e["num"])

check_keys = [
    "stats", 
    "type",
    "moves",
    "abilities"
]

stats = [
    "HP",
    "Atk",
    "Def",
    "SpA",
    "SpD",
    "Spe",
    "BST",
]

for entry in all_data:
    for key in check_keys:
        if key not in entry:
            print(entry["name"], entry.get("region", ""), "has no", key)

    if "stats" in entry:
        for stat in stats:
            if stat not in entry["stats"]:
                print(entry["name"], entry.get("region", ""), "has no stat", stat)
