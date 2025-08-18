import winrates
from league_types import *

def test_azir_wr():
	actual = winrates.get_winrate_for_champ_in_role_in_tier('azir', TeamPosition.Mid, 'Gold')
	print(actual)
	assert actual is not None