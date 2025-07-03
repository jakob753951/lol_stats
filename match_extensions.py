from league_types import *
from pulsefire.schemas import RiotAPISchema

def get_match_gamemode(match: RiotAPISchema.LolMatchV5Match):
	return Gamemode(match["info"]["gameMode"])

def get_champ_and_role_and_win_from_match_and_puuid(match: RiotAPISchema.LolMatchV5Match, puuid: str):
	participant_index = match["metadata"]["participants"].index(puuid)
	participant = match["info"]["participants"][participant_index]
	team = next(team for team in match['info']['teams'] if team['teamId'] == participant['teamId'])
	champ = participant["championName"]
	team_position = participant["teamPosition"]
	role = TeamPosition(team_position)
	did_win = team["win"]
	return champ, role, did_win

def match_was_remake(match: RiotAPISchema.LolMatchV5Match):
	return match['info']['participants'][0]['gameEndedInEarlySurrender']

def get_match_game_version(match: RiotAPISchema.LolMatchV5Match) -> GameVersion:
	parts = [int(part) for part in match['info']['gameVersion'].split('.')]
	return GameVersion(*parts)