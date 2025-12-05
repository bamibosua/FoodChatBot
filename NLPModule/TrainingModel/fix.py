import json

with open("train_data.jsonl", "r", encoding="utf8") as f:
    for i, line in enumerate(f, 1):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"Error on line {i}: {e}")
            print("Line content:", line)