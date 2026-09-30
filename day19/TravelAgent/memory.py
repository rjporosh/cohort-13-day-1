import json
import os
import re
import time
from typing import Any, Optional


class CustomerMemory:
    """Small JSON-backed, customer-isolated memory and cache."""

    def __init__(self, root: str = "memory"):
        self.root = root
        os.makedirs(self.root, exist_ok=True)

    def _path(self, customer_id: int) -> str:
        if customer_id == 0:
            return os.path.join(self.root, "routing.json")
        return os.path.join(self.root, f"customer_{customer_id}.json")

    def _load(self, customer_id: int) -> dict:
        path = self._path(customer_id)
        if not os.path.exists(path):
            return {
                "customer_id": customer_id,
                "memory": {},
                "cache": {}
            }
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if data.get("customer_id") != customer_id:
                return {"customer_id": customer_id, "memory": {}, "cache": {}}
            return data
        except (OSError, json.JSONDecodeError):
            return {"customer_id": customer_id, "memory": {}, "cache": {}}

    def _save(self, customer_id: int, data: dict) -> None:
        path = self._path(customer_id)
        temporary = f"{path}.tmp"
        with open(temporary, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        os.replace(temporary, path)

    def get(self, customer_id: int, key: str) -> Optional[Any]:
        return self._load(customer_id)["memory"].get(key)

    def save(self, customer_id: int, key: str, value: str) -> dict:
        data = self._load(customer_id)
        data["memory"][key] = value
        self._save(customer_id, data)
        return {"status": "saved", "key": key, "value": value}

    def retrieve(self, customer_id: int, query: str) -> dict:
        data = self._load(customer_id)
        words = set(re.findall(r"\w+", query.lower()))
        matches = []

        for key, value in data["memory"].items():
            searchable = f"{key.replace('_', ' ')} {value}".lower()
            if words.intersection(set(re.findall(r"\w+", searchable))):
                matches.append({"key": key, "value": value})

        return {"query": query, "matches": matches}

    def get_cached(self, customer_id: int, key: str) -> Optional[Any]:
        return self._load(customer_id)["cache"].get(key)

    def set_cached(self, customer_id: int, key: str, value: Any) -> None:
        data = self._load(customer_id)
        data["cache"][key] = value
        self._save(customer_id, data)

    def delete_cached(self, customer_id: int, key: str) -> None:
        data = self._load(customer_id)
        data["cache"].pop(key, None)
        self._save(customer_id, data)
