from functools import cache
import json
import os
from typing import Any
import requests


champions_folder_path = 'cache/static_data'
champions_file_path = f'{champions_folder_path}/champions.json'
champions_api_url = 'https://ddragon.leagueoflegends.com/cdn/15.13.1/data/en_US/champion.json'

def get_champions() -> dict[str, dict[str, Any]]:
	if os.path.exists(champions_file_path):
		with open(champions_file_path, encoding='utf-8') as f:
			return json.load(f)
	else:
		response = requests.get(champions_api_url)
		champ_data = json.loads(response.text)

		if not os.path.exists(champions_file_path):
			if not os.path.exists(champions_folder_path):
				os.makedirs(champions_folder_path)
			with open(champions_file_path, 'w', encoding='utf-8') as f:
				json.dump(champ_data, f)
		return champ_data
	

@cache
def get_champion(champ_id: str) -> dict[str, Any] | None:
	champs_data = get_champions()

	# When getting Fiddlesticks from a game, he'll be called FiddleSticks. Don't ask me why
	if champ_id == 'FiddleSticks': champ_id = 'Fiddlesticks'
	
	return champs_data['data'].get(champ_id, None)

@cache
def get_champion_name(champ_id: str) -> str | None:
	champ = get_champion(champ_id)
	if champ is None: return None
	return champ.get('name', 'Unknown')
