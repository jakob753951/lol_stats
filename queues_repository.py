from functools import cache
import json
import os
from typing import Any
import requests
from league_types import Queue

queues_folder_path = 'cache/static_data'
queues_file_path = f'{queues_folder_path}/queues.json'
queues_api_url = 'https://ddragon.leagueoflegends.com/cdn/15.13.1/data/en_US/champion.json'

def get_queues() -> dict[int, Queue]:
	if os.path.exists(queues_file_path):
		with open(queues_file_path, encoding='utf-8') as f:
			queue_data: list[dict[str, Any]] = json.load(f)
	else:
		response = requests.get(queues_api_url)
		queue_data: list[dict[str, Any]] = json.loads(response.text)

		if not os.path.exists(queues_file_path):
			if not os.path.exists(queues_folder_path):
				os.makedirs(queues_folder_path)
			with open(queues_file_path, 'w', encoding='utf-8') as f:
				json.dump(queue_data, f)
	
	queues = {queue['queueId']: Queue.from_dict(queue) for queue in queue_data}
	
	return queues

@cache
def get_queue_by_id(queue_id: int) -> Queue | None:
	queues_data = get_queues()
	return queues_data.get(queue_id, None)