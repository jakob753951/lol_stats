from functools import cache
import json


champions_file_path = 'champions.json'

@cache
def get_champion_data(champ_id: str) -> dict | None:
	with open(champions_file_path, encoding='utf-8') as f:
		champs_data = json.load(f)
	# When getting Fiddlesticks from a game, he'll be called FiddleSticks. Don't ask me why
	if champ_id == 'FiddleSticks': champ_id = 'Fiddlesticks'
	
	return champs_data['data'].get(champ_id, None)

@cache
def get_champion_name(champ_id: str) -> str | None:
	champ = get_champion_data(champ_id)
	if champ is None: return None
	return champ.get('name', 'Unknown')
