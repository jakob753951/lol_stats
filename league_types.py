from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple

class Gamemode(Enum):
	Arena = 'CHERRY'
	Classic = 'CLASSIC'
	Swiftplay = 'SWIFTPLAY'
	Aram = 'ARAM'
	Urf = 'URF'
	PracticeTool = 'PRACTICETOOL'

class TeamPosition(Enum):
	Top = 'TOP'
	Jungle = 'JUNGLE'
	Mid = 'MIDDLE'
	Marksman = 'BOTTOM'
	Support = 'UTILITY'

class QueueType(Enum):
	Solo = 'RANKED_SOLO_5x5'
	Flex = 'RANKED_FLEX_5x5'

@dataclass
class Queue:
	queueId: int
	map: str
	description: str
	notes: str

class RiotId(NamedTuple):
	game_name: str
	tag_line: str
	
	@staticmethod
	def from_str(user_name: str) -> 'RiotId':
		user_name_parts = user_name.split('#')
		if len(user_name_parts) == 1:
			game_name, tag_line = (user_name, 'EUW')
		else:
			game_name, tag_line = user_name_parts
		return RiotId(game_name, tag_line)


@dataclass
class GameVersion:
	major: int
	minor: int
	patch: int
	build: int
	pass

	@staticmethod
	def major_equal(a: 'GameVersion', b: 'GameVersion') -> bool:
		return a.major == b.major

	@staticmethod
	def minor_equal(a: 'GameVersion', b: 'GameVersion') -> bool:
		return GameVersion.major_equal(a, b) and a.minor == b.minor

	@staticmethod
	def patch_equal(a: 'GameVersion', b: 'GameVersion') -> bool:
		return GameVersion.minor_equal(a, b) and a.patch == b.patch