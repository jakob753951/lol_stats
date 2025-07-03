from math import comb

def P(k, n, p):
	return comb(n, k) * p**k * (1-p)**(n-k)

def get_p_value(games_played_on_champion: int, games_won_on_champion: int, champion_winrate: float) -> float:
	p = champion_winrate
	M = games_played_on_champion
	N = games_won_on_champion
	return sum(P(k, M, p) for k in range(N, M+1))