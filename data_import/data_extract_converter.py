from collections import defaultdict
import json
from league_types import *

# Unranked is the average from all games, rank irrelevant
tiers = ['unranked', 'silver', 'gold', 'platinum', 'emerald']
for tier in tiers:
	with open(f'data_extract_{tier}.json') as f:
		champs: list = json.load(f)
		# is in the format list[ChampData]
		# where ChampData is is a simple object with these fields:
		# "name": "Aatrox",
		# "role": "supp",
		# "pickrate": 0.01,
		# "winrate": 0.4118

	converted_champs = defaultdict(lambda: defaultdict(float))

	with open('champ_names_to_ids.json') as f:
		champ_name_to_id = json.load(f)

	for champ in champs:
		match champ['role']:
			case 'top': role = TeamPosition.Top
			case 'jung': role = TeamPosition.Jungle
			case 'mid': role = TeamPosition.Mid
			case 'bot': role = TeamPosition.Marksman
			case 'supp': role = TeamPosition.Support
		converted_champs[champ_name_to_id[champ['name']].lower()][role.name] = champ['winrate']


	with open(f'champion_winrates_{tier}.json', 'w') as f:
		json.dump(converted_champs, f, indent=4)