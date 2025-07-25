import os
from league_types import *
import json

def get_winrate_for_champ_in_role_in_tier(champ_id: str, role: TeamPosition, tier: str) -> float:
	winrates_file_path = f'champion_winrates_{tier}.json'
	if not os.path.exists(winrates_file_path):
		return 0.5
	with open(winrates_file_path) as f:
		champs = json.load(f)
	return champs[champ_id.lower()][role.name]
