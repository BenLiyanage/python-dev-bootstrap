import json
import pandas

with open('guest_cards.json', 'r') as file:
    guest_cards = pandas.DataFrame(json.loads(file.read()))

print guest_cards