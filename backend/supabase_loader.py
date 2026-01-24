from __future__ import annotations

import json
import math
import urllib.request
from typing import Iterable


class SupabaseClient:
    def __init__(self, base_url: str, service_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.service_key = service_key

    def upsert(self, table: str, rows: Iterable[dict], batch_size: int = 500) -> None:
        rows_list = list(rows)
        if not rows_list:
            return
        batches = math.ceil(len(rows_list) / batch_size)
        for i in range(batches):
            batch = rows_list[i * batch_size : (i + 1) * batch_size]
            self._post_batch(table, batch)

    def _post_batch(self, table: str, batch: list[dict]) -> None:
        url = f"{self.base_url}/rest/v1/{table}"
        headers = {
            "Content-Type": "application/json",
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Prefer": "resolution=merge-duplicates,return=representation",
        }
        request = urllib.request.Request(
            url=url,
            data=json.dumps(batch).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request) as response:
            response.read()
