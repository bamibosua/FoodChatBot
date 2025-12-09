import spacy
import random
import json
from spacy.matcher import Matcher
from spacy.training.example import Example
from spacy.util import minibatch

def load_train_data(path):
    data = []
    with open(path, "r", encoding="utf8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                print(f"Dòng {line_no} rỗng → bỏ qua")
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                print(f"JSON lỗi ở dòng {line_no}: {line}")
                continue

            # item phải là list có 2 phần tử
            if not isinstance(item, list) or len(item) != 2:
                print(f"Sai format ở dòng {line_no}: {item}")
                continue

            text, ann = item

            if not isinstance(text, str):
                print(f"Text không phải string ở dòng {line_no}")
                continue

            if not isinstance(ann, dict) or "entities" not in ann:
                print(f"Annotation sai format ở dòng {line_no}")
                continue

            data.append((text.lower(), {"entities": ann["entities"]}))
    return data

train_data = load_train_data("train_datas.jsonl")

nlp = spacy.load("en_core_web_md")

ruler = nlp.add_pipe("entity_ruler", before="ner")

foodPatterns = [
    "vermicelli with tofu",
    "snails",
    "banh mi",
    "crab noodle soup",
    "steamed rice rolls",
    "grilled pork vermicelli",
    "crab thick noodle soup",
    "pho",
    "pork rib porridge",
    "water fern cakes",
    "wet rice cakes",
    "vegetarian food",
    "broken rice",
    "sizzling beef",
    "grilled chicken",
    "sticky rice sweet soup",
    "vietnamese pancake",
    "hue beef noodle",
    "grilled pork sausage",
    "chicken rice",
    "beef rice",
    "chicken sticky rice",
    "steamed rice cake",
    "herbal chicken stew",
    "milo",
    "chicken hot pot",
    "beef hot pot",
    "beef stew pho",
    "thick noodle soup",
    "offal porridge",
    "vegetarian noodle",
    "plain porridge",
    "wet cake with grilled pork",
    "fermented fish hot pot",
    "frog porridge",
    "banh mi with fish cake",
    "fermented fish noodle",
    "fried noodles",
    "grilled food",
    "mini pancakes",
    "grilled pork with noodle",
    "fish porridge",
    "beef ball noodle",
    "noodle soup",
    "beef jerky salad",
    "fried flour cubes",
    "goby fish hot pot",
    "grilled banana sticky rice",
    "sweet soup",
    "thai noodle",
    "fried rice",
    "squid noodle",
    "fish noodle",
    "noodle and egg noodle",
    "phnom penh noodle",
    "chicken",
    "fermented pork",
    "rice noodle with shredded skin",
    "hot pot",
    "herbal soup",
    "cade sticky rice",
    "duck noodle soup",
    "crab sticky rice",
    "dimsum",
    "dumplings",
    "noodles",
    "instant noodle with beef balls",
    "rice",
    "broth noodle",
    "mixed porridge",
    "roast chicken rice",
    "goat noodle",
    "ginseng",
    "shrimp dumplings",
    "bitter melon",
    "steamed rice rolls with squid cake",
    "wet cake with chicken organs",
    "beef sticky rice",
    "grilled fish",
    "young beef",
    "sticky rice",
    "chicken duck porridge",
    "grilled corn",
    "stingray hot pot",
    "fish and snail noodle",
    "stirred vermicelli",
    "crab soup",
    "coconut ice cream",
    "duck thick noodle soup",
    "pork rolls",
    "spring rolls",
    "snakehead fish thick noodle",
    "grilled octopus",
    "fried tofu with pepper salt",
    "broken rice with pork",
    "german sausages",
    "mini rice cakes",
    "vegetarian noodle soup",
    "duck salad",
    "goat hot pot",
    "chive thick noodle soup",
    "fish noodle soup",
    "dry pho",
    "pork skewers",
    "fish thick noodle soup",
    "rice with egg",
    "black chicken",
    "tofu pudding",
    "chicken curry",
    "eel congee",
    "vinegar beef hot pot",
    "squid noodle soup",
    "steamed buns",
    "beef in betel leaves",
    "quang style noodles",
    "duck porridge",
    "noodle soup with satay shrimp",
    "seafood noodle soup",
    "tea",
    "vegetarian rice",
    "grilled pork with noodles",
    "goat noodle soup",
    "wet cake",
    "pork rib congee",
    "balut",
    "noodle with pork ribs",
    "shrimp dumpling",
    "satay noodle soup",
    "vietnamese beef steak",
    "noodle with tofu and shrimp paste",
    "roasted duck",
    "offal congee",
    "chicken noodle soup",
    "quang noodles",
    "eel congee",
    "snakehead fish thick noodle",
    "vermicelli", "tofu", "snail", "snails", "banh", "mi",
    "crab", "noodle", "soup", "rice", "rolls", 
    "pork", "thick", "cake", "beef", "ball",
    "porridge", "sweet", "fish", "chicken", "shrimp",
    "duck", "frog", "goat", "octopus", "pancake",
    "dumpling", "dumplings", "pot", "sticky",
    "beef", "beefball", "congee", "ice", "cream",
    "salad", "squid", "herbal", "ginseng", "vegetarian",
    "pudding", "tofu", "corn", "soup", "tea",
    "roll", "rolls", "cake", "cakes"
]

food_patterns = []
for food in foodPatterns:
    tokens = food.lower().split()
    pattern = [{"LOWER": t} for t in tokens]
    food_patterns.append({"label": "FOOD", "pattern": pattern})

budget_patterns_numbers = [
    {"label": "BUDGET", "pattern": [{"TEXT": {"REGEX": "^[0-9]{2,3}k$"}}]},
    {"label": "BUDGET", "pattern": [{"TEXT": {"REGEX": "^[0-9]{2,3}k vnd$"}}]},
    {"label": "BUDGET", "pattern": [{"TEXT": {"REGEX": "^[0-9]{2,3}k-[0-9]{2,3}k$"}}]},
    {"label": "BUDGET", "pattern": [{"TEXT": {"REGEX": "^[0-9]{2,3}k-[0-9]{2,3}k vnd$"}}]},
]

budget_patterns_simple = [
    {"label": "BUDGET", "pattern": [
        {"LOWER": {"IN": ["fifty", "sixty", "seventy", "eighty", "ninety"]}},
        {"LOWER": {"IN": ["thousand", "k"]}},
        {"LOWER": {"IN": ["vnd", "dong", "$", "usd"]}, "OP": "?"}
    ]},
    {"label": "BUDGET", "pattern": [
        {"LOWER": {"IN": ["one", "a"]}},
        {"LOWER": "hundred"},
        {"LOWER": {"IN": ["thousand", "k"]}, "OP": "?"},
        {"LOWER": {"IN": ["vnd", "dong", "$", "usd"]}, "OP": "?"}
    ]},
    {"label": "BUDGET", "pattern": [
        {"LOWER": {"IN": ["twenty", "thirty", "forty", "fifty"]}},
        {"LOWER": {"IN": ["one", "two", "three", "five", "zero"]}, "OP": "?"},
        {"LOWER": {"IN": ["thousand", "k"]}}
    ]},
]

budget_patterns_limits = [
    {"label": "BUDGET", "pattern": [
        {"LOWER": {"IN": ["fifty", "sixty", "seventy", "eighty", "ninety", "one"]}},
        {"LOWER": {"IN": ["k", "thousand", "hundred"]}, "OP": "?"},
        {"LOWER": {"IN": ["vnd", "dong", "$", "usd"]}, "OP": "?"}
    ]}
]

budget_patterns_range = [
    {"label": "BUDGET", "pattern": [
        {"LOWER": {"IN": ["fifty", "sixty", "seventy"]}},
        {"LOWER": {"IN": ["k", "thousand"]}, "OP": "?"},
        {"LOWER": {"IN": ["to", "and", "-"]}},
        {"LOWER": {"IN": ["eighty", "ninety", "one"]}},
        {"LOWER": {"IN": ["k", "thousand", "hundred"]}, "OP": "?"},
        {"LOWER": {"IN": ["vnd", "dong", "$", "usd"]}, "OP": "?"}
    ]}
]

budget_patterns = (
    budget_patterns_numbers
    + budget_patterns_simple
    + budget_patterns_limits
    + budget_patterns_range
)

districts = [
    "binh thanh district", "go vap district", "tan binh district", "phu nhuan district",
    "binh tan district", "tan phu district", "thu duc district",
    "district 1","district 2","district 3","district 4","district 5",
    "district 6","district 7","district 8","district 9","district 10",
    "district 11","district 12"
]

district_short = ["binh thanh"]

location_patterns = []
for d in districts + district_short:
    tokens = d.lower().split()
    location_patterns.append({"label": "LOCATION", "pattern": [{"LOWER": t} for t in tokens]})

cities_vn = [
    "ho chi minh", "ha noi", "da nang", "can tho", 
    "hai phong", "hue", "nha trang", "vung tau"
]

matcher = Matcher(nlp.vocab)
city_patterns = []

for city in cities_vn:
    tokens = city.split()
    pattern = [{"LOWER": t.lower()} for t in tokens]
    city_patterns.append({"label": "CITY", "pattern": pattern})

ruler.add_patterns(food_patterns + budget_patterns + location_patterns + city_patterns)

if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner")
else:
    ner = nlp.get_pipe("ner")

for text, annot in train_data:
    for start, end, label in annot["entities"]:
        if label not in ["BUDGET", "LOCATION", "CITY"]:
            ner.add_label(label)

other_pipes = [p for p in nlp.pipe_names if p != "ner"]

patience = 5
no_improve_epochs = 0
best_loss = float("inf")

with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.resume_training()
    n_iter = 100

    for epoch in range(n_iter):
        random.shuffle(train_data)
        losses = {}
        batches = minibatch(train_data, size=4)

        for batch in batches:
            examples = []
            for text, annotations in batch:
                doc = nlp.make_doc(text)
                examples.append(Example.from_dict(doc, annotations))
            nlp.update(examples, drop=0.2, sgd=optimizer, losses=losses)

        current_loss = losses.get("ner", sum(losses.values()))
        print(f"Epoch {epoch+1}/{n_iter} - Loss: {current_loss}")

        # --- EARLY STOPPING ---
        if current_loss < best_loss:
            best_loss = current_loss
            no_improve_epochs = 0
        else:
            no_improve_epochs += 1
            print(f"➡️  No improvement for {no_improve_epochs} epoch(s)")

        if no_improve_epochs >= patience:
            print("🛑 Early stopping triggered!")
            break

nlp.to_disk("../custom_ner_model")
print("Model saved to 'custom_ner_model'")