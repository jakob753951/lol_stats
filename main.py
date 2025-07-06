import asyncio
from collections import defaultdict
from dataclasses import dataclass
import json
import os
from typing import Any, AsyncIterator
from pulsefire.clients import RiotAPIClient
from pulsefire.schemas import RiotAPISchema
from league_types import *
import player_statistics
from winrates import get_winrate_for_champ_in_role_in_tier
import match_repository
import champions_repository
from aioitertools.itertools import takewhile
from match_extensions import *

# INTERACTIVE = sys.stdin.isatty()
INTERACTIVE = False
DEBUG = True

def log_debug(message: str = ''):
	if DEBUG: print(message)

def log_interactive(message: str = ''):
	if INTERACTIVE: print(message)

def log_cli(message: str = ''):
	if not INTERACTIVE: print(message)

async def get_summoner(client: RiotAPIClient, game_name: str, tag_line: str) -> RiotAPISchema.LolSummonerV4Summoner:
	account = await client.get_account_v1_by_riot_id(region="europe", game_name=game_name, tag_line=tag_line)
	summoner = await client.get_lol_summoner_v4_by_puuid(region="euw1", puuid=account["puuid"])
	return summoner

def get_profile_icon_url_by_id(profile_icon_id: int) -> str:
	return f'https://ddragon.leagueoflegends.com/cdn/15.12.1/img/profileicon/{profile_icon_id}.png'

def get_queue_rank_from_leagues(leagues: list[RiotAPISchema.LolLeagueV4LeagueFullEntry], queue: Queue):
	for league in leagues:
		if league["queueType"] == queue.value:
			return (league["tier"], league["rank"])

async def match_generator(client: RiotAPIClient, puuid: str):
	PAGE_SIZE = 100
	i = 0
	while True:
		page_match_ids: list[str] = await client.get_lol_match_v5_match_ids_by_puuid(region="europe", puuid=puuid, queries={'start': i, 'count': PAGE_SIZE})
		i += PAGE_SIZE
		for match_id in page_match_ids:
			match = await match_repository.get_match_by_id(client, match_id)
			if match is None:
				continue
			yield match

@dataclass
class ChampionStat:
	wins: int
	games: int

@dataclass(frozen=True)
class ChampRoleStat:
	user: str
	wins: int
	games: int
	champ_id: str
	champ_name: str
	role: TeamPosition
	tier: str
	def __str__(self) -> str:
		return f'{self.champ_name} {self.role.name}: {self.wins}/{self.games} = {self.get_player_winrate():.02f}% p-value: {self.get_p_value():.02f}%'

	def to_json(self) -> str:
		return json.dumps(self.to_output_dict())
	
	def to_output_dict(self) -> dict[str, Any]:
		return {
			'name': self.champ_name,
			'role': self.role.name,
			'wins': self.wins,
			'games': self.games,
			'player_winrate': f'{self.get_player_winrate() * 100:6.02f}%',
			f'global_winrate_in_{self.tier.lower()}': f'{self.get_global_winrate() * 100:6.02f}%',
			'p-value': self.get_p_value(),
		}

	def get_p_value(self) -> float:
		return player_statistics.get_p_value(self.games, self.wins, self.get_global_winrate())

	def get_global_winrate(self) -> float:
		return get_winrate_for_champ_in_role_in_tier(self.champ_id, self.role, self.tier)

	def get_player_winrate(self) -> float:
		return self.wins/self.games


api_key = os.environ['RIOT_API_KEY']
async def main():
	if INTERACTIVE:
		players: list[str] = []
		while True:
			user_input = input('Enter Riot ID or empty to stop: ')
			if user_input == '' or user_input.isspace():
				break
			players.append(user_input)
	else:
		with open('players.json', encoding='UTF-8') as f:
			players = json.load(f)
		
	# players = ['xferm', 'jakob moeller', 'sarcasm chief#lau', 'rostbøll', 'nuggy', 'hexactly', 'shadowmik#7153', 'admiral adc', 'flx thurcaye', 'brk#42069']
	async with RiotAPIClient(default_headers={"X-Riot-Token": api_key}) as client:
		player_champ_role_stats: dict[str, list[ChampRoleStat]] = {}
		for player in players:
			player_champ_role_stats[player] = await stats_by_champ_and_role_for_user(client, player)
		
	log_cli(json.dumps({player: [champ_role_stat.to_output_dict() for champ_role_stat in champ_role_stats] for player, champ_role_stats in player_champ_role_stats.items()}))
	if INTERACTIVE:
		for player, champ_role_stats in player_champ_role_stats.items():
			champ_role_stats.sort(key=lambda champ: champ.get_p_value())
			log_interactive()
			log_interactive(f'Player "{player}":')
			log_interactive('\n'.join(str(champ_role_stat) for champ_role_stat in champ_role_stats))


async def stats_by_champ_and_role_for_user(client: RiotAPIClient, user_name: str) -> list[ChampRoleStat]:
	(game_name, tag_line) = RiotId.from_str(user_name)
	account = await client.get_account_v1_by_riot_id(region="europe", game_name=game_name, tag_line=tag_line)
	puuid = account["puuid"]
	leagues = await client.get_lol_league_v4_entries_by_puuid(region="euw1", puuid=puuid)
	(tier, _) = get_queue_rank_from_leagues(leagues, Queue.Solo) or ('Unranked', 'Unranked')
	
	current_version = GameVersion(15, 13, 693, 4876)
	
	matches = match_generator(client, puuid)
	matches = takewhile(
		lambda match: GameVersion.major_equal(get_match_game_version(match), current_version),
		matches
	)
	# log_interactive(f'found {len([match async for match in matches if get_match_gamemode(match) == Gamemode.Classic and not match_was_remake(match)])} games from season {current_version.major}')
	champion_stats: defaultdict[str, defaultdict[TeamPosition, ChampionStat]] = defaultdict(lambda: defaultdict(lambda: ChampionStat(0, 0)))
	async for match in matches:
		if match_was_remake(match): continue
		if get_match_gamemode(match) != Gamemode.Classic: continue
		champ_id, role, did_win = get_champ_and_role_and_win_from_match_and_puuid(match, puuid)
		champion_stats[champ_id][role].games += 1
		if did_win:
			champion_stats[champ_id][role].wins += 1
	
	champ_role_stats: list[ChampRoleStat] = []
	for champ_id, roles in champion_stats.items():
		champ_name = champions_repository.get_champion_name(champ_id)
		if champ_name is None: champ_name = champ_id
		for role, stat in roles.items():
			champ_role_stats.append(ChampRoleStat(user_name, stat.wins, stat.games, champ_id, champ_name, role, tier))
	return champ_role_stats

asyncio.run(main())