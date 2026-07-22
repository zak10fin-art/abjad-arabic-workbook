import json

from config.config import BOOK

print("=" * 40)
print("Abjad Arabic Academy")
print("Workbook Generator")
print("=" * 40)

print("Book Title:", BOOK["title"])

with open("data/alphabet.json", "r", encoding="utf-8") as file:
    alphabet = json.load(file)

print("Data loaded successfully!")
print("Number of letters:", len(alphabet))

for letter in alphabet:
    print("----------------")
    print("Letter:", letter["letter"])
    print("Name:", letter["name"])
    print("Pronunciation:", letter["pronunciation"])


