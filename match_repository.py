import json
import os
from aiohttp import ClientResponseError
from pulsefire.schemas import RiotAPISchema
from pulsefire.clients import RiotAPIClient
import asyncio

def get_file_path_from_match_id(match_id: str) -> str:
    return f"cache/match_{match_id}.json"


def save_match(match: RiotAPISchema.LolMatchV5Match):
    file_path = get_file_path_from_match_id(match["metadata"]["matchId"])
    with open(file_path, "w") as f:
        json.dump(match, f)


def load_match(match_id: str) -> RiotAPISchema.LolMatchV5Match | None:
    file_path = get_file_path_from_match_id(match_id)
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        return json.load(f)


async def get_match_by_id(
    client: RiotAPIClient, match_id: str
) -> RiotAPISchema.LolMatchV5Match | None:
    cached_match = load_match(match_id)
    if cached_match is not None:
        return cached_match
    try:
        await asyncio.sleep(0.5)
        match = await client.get_lol_match_v5_match(region="europe", id=match_id)
        save_match(match)
        return match
    except ClientResponseError:
        return None
