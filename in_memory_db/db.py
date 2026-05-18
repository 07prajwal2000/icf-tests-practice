import copy
from heapq import heappop, heappush, heapify

NO_TTL = -1


class Field:
    def __init__(self, key: str, field: str, value: str):
        self.key = key
        self.field = field
        self.value = value
        self.ttl = NO_TTL

    def set_ttl(self, ttl: int):
        self.ttl = ttl

    def __lt__(self, other: "Field"):
        return other.ttl > self.ttl

    def __str__(self):
        return f"{self.key}: {self.field}={self.value} TTL={self.ttl}"


class DBData:
    def __init__(self, key: str):
        self.key = key
        self.fields: dict[str, Field] = {}

    def get(self, field: str) -> Field:
        return self.fields[field]

    def set(self, field: str, value: str):
        self.fields[field] = Field(key=self.key, field=field, value=value)

    def set_with_ttl(self, field: str, value: str, ttl: int):
        self.set(field=field, value=value)
        self.get(field=field).set_ttl(ttl=ttl)

    def delete(self, field: str):
        del self.fields[field]

    def exists(self, field: str) -> bool:
        return field in self.fields


class Backup:
    def __init__(
        self, backedup_on: int, db: dict[str, DBData], ttl_fields: list[Field]
    ):
        self.backedup_on = backedup_on
        self.db = db
        self.ttl_fields = ttl_fields


class InMemoryDB:
    def __init__(self):
        self.db: dict[str, DBData] = {}
        self.ttl_fields: list[Field] = []
        self.backups: list[Backup] = []

    def set(self, key: str, field: str, value: str) -> str:
        if not self._does_key_exist(key=key):
            self.db[key] = DBData(key=key)
        self.db[key].set(field=field, value=value)
        return ""

    def get(self, key: str, field: str) -> str:
        if not self._does_field_exist(key=key, field=field):
            return ""
        return self.db[key].get(field=field).value

    def delete(self, key: str, field: str) -> str:
        if not self._does_field_exist(key=key, field=field):
            return "false"
        self.db[key].delete(field=field)
        return "true"

    def scan(self, key: str) -> str:
        if not self._does_key_exist(key=key):
            return ""
        result = self._get_field_value_pair(key=key, sort_items=True)
        output = self._format_items(items=result)
        return output

    def scan_by_prefix(self, key: str, prefix: str) -> str:
        if not self._does_key_exist(key=key):
            return ""
        result = self._get_field_value_pair(
            key=key, sort_items=True, filter_by_prefix=prefix
        )
        output = self._format_items(items=result)
        return output

    def set_at(self, key: str, field: str, value: str, timestamp: int) -> str:
        self._on_timestamp_event(timestamp=timestamp)
        return self.set(key=key, field=field, value=value)

    def set_at_with_ttl(
        self, key: str, field: str, value: str, timestamp: int, ttl: int
    ) -> str:
        self._on_timestamp_event(timestamp=timestamp)
        self.set(key=key, field=field, value=value)
        calculated_ttl = timestamp + ttl
        ttl_field = self.db[key].get(field=field)
        ttl_field.set_ttl(ttl=calculated_ttl)
        self._delete_ttl_field(key=key, field=field)
        heappush(self.ttl_fields, ttl_field)
        return ""

    def delete_at(self, key: str, field: str, timestamp: int) -> str:
        self._on_timestamp_event(timestamp=timestamp)
        delete_result = self.delete(key=key, field=field)
        if delete_result == "false":
            return delete_result
        self._delete_ttl_field(key=key, field=field)
        return delete_result

    def get_at(self, key: str, field: str, timestamp: int) -> str:
        self._on_timestamp_event(timestamp=timestamp)
        return self.get(key=key, field=field)

    def scan_by_prefix_at(self, key, prefix, timestamp: int) -> str:
        self._on_timestamp_event(timestamp=timestamp)
        return self.scan_by_prefix(key=key, prefix=prefix)

    def backup(self, timestamp: int):
        self._on_timestamp_event(timestamp=timestamp)
        deep_copy_db = copy.deepcopy(self.db)
        deep_copy_ttl_fields = copy.deepcopy(self.ttl_fields)
        new_backup = Backup(timestamp, deep_copy_db, deep_copy_ttl_fields)
        self.backups.append(new_backup)
        self.backups.sort(key=lambda x: x.backedup_on, reverse=True)
        return str(len(self.ttl_fields))

    def restore(self, timestamp: int, timestampToRestore: int) -> str:
        backup_to_restore = None
        for backup in self.backups:
            if backup.backedup_on <= timestampToRestore:
                backup_to_restore = backup
                break
        if backup_to_restore is None:
            return ""
        self.db = copy.deepcopy(backup_to_restore.db)
        self.ttl_fields = copy.deepcopy(backup_to_restore.ttl_fields)
        self._on_timestamp_event(timestamp=timestamp)
        return ""

    def _on_timestamp_event(self, timestamp: int):
        if len(self.ttl_fields) == 0 or self.ttl_fields[0].ttl > timestamp:
            return
        deleted_keys: set[str] = set()
        while len(self.ttl_fields) > 0 and self.ttl_fields[0].ttl <= timestamp:
            removed_field = heappop(self.ttl_fields)
            deleted_keys.add(f"{removed_field.key}:{removed_field.field}")
        self._delete_ttl_field(field_list_to_delete_from=deleted_keys)

    def _delete_ttl_field(
        self, key: str, field: str, field_list_to_delete_from: set[str] = None
    ):
        if field_list_to_delete_from is None:
            field_list_to_delete_from = {f"{key}:{field}"}
        self.ttl_fields = [
            field
            for field in self.ttl_fields
            if f"{field.key}:{field.field}" not in field_list_to_delete_from
        ]
        heapify(self.ttl_fields)

    def _format_items(self, items: list[Field]):
        result = []
        for item in items:
            result.append(f"{item.field}({item.value})")
        return ", ".join(result)

    def _does_key_exist(self, key: str) -> bool:
        return key in self.db

    def _does_field_exist(self, key: str, field: str) -> bool:
        return self._does_key_exist(key=key) and self.db[key].exists(field=field)

    def _get_field_value_pair(
        self, key: str, sort_items=False, filter_by_prefix: str = ""
    ) -> list[Field]:
        result: list[Field] = []
        db_subset = self.db[key].fields
        for field, value in db_subset.items():
            if filter_by_prefix != "" and not field.startswith(filter_by_prefix):
                continue
            result.append(value)
        if sort_items:
            result.sort(key=lambda x: x.field)
        return result
