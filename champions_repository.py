from functools import cache
import json


champions_file_path = 'champions.json'

@cache
def get_champion_data(champ_id: str) -> dict:
	with open(champions_file_path, encoding='utf-8') as f:
		champs_data = json.load(f)
	# When getting Fiddlesticks from a game, he'll be called FiddleSticks. Don't ask me why
	if champ_id == 'FiddleSticks': champ_id = 'Fiddlesticks'
	
	return champs_data['data'][champ_id]

@cache
def get_champion_name(champ_id: str) -> str:
	champ = get_champion_data(champ_id)
	return champ.get('name', 'Unknown')
