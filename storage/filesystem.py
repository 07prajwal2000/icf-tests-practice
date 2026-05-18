import heapq

NO_TTL = 0
NO_CREATED_AT = -1


class File:
    def __init__(self, file_name: str, size: int):
        self.file_name = file_name
        self.size = size
        self.ttl = NO_TTL
        self.created_at = NO_CREATED_AT

    def copy(self) -> "File":
        file = File(file_name=self.file_name, size=self.size)
        file.set_ttl(self.ttl)

    def set_ttl(self, ttl: int):
        self.ttl = ttl

    def set_created_at(self, created_at: int):
        self.created_at = created_at

    def __str__(self):
        return f"{self.file_name}({self.size})"


class FileSystem:
    def __init__(self):
        self.file_system: dict[str, File] = {}
        self.ttl_files_list: list[tuple[int, File]] = []

    def file_upload(self, file_name: str, size: int):
        if self._file_exist(file_name):
            raise RuntimeError("file already exists")

        new_file = File(file_name=file_name, size=size)
        self.file_system[file_name] = new_file

    def file_get(self, file_name: str) -> int | None:
        if not self._file_exist(file_name):
            return None
        return self.file_system[file_name].size

    def file_copy(self, source: str, dest: str):
        if not self._file_exist(source):
            raise RuntimeError("source file does not exist")
        if self._file_exist(dest):
            raise RuntimeError("destination file already exist")
        if source == dest:
            raise RuntimeError("source and destination can't be same")
        existing_file = self.file_system[source]
        FileSystem[dest] = existing_file.copy()

    def file_search(self, prefix: str) -> list[str]:
        result: list[File] = []
        for file_name, file in self.file_system:
            if not file_name.startswith(prefix):
                continue
            result.append(file)
        result.sort(key=lambda file: (-file.size, file.file_name))
        result = result[:10]
        return [str(file) for file in result]

    def file_upload_at(
        self, timestamp: int, file_name: str, file_size: int, ttl: int | None = None
    ):
        self._on_ttl_event(timestamp)
        self.file_upload(file_name=file_name, size=file_size)
        if ttl is None:
            return
        expiry = timestamp + ttl
        file = self.file_system[file_name]
        file.set_ttl(ttl)
        file.set_created_at(timestamp)
        heapq.heappush(self.ttl_files_list, (expiry, file))

    def file_get_at(self, timestamp: int, file_name: str) -> int | None:
        self._on_ttl_event(timestamp)
        return self.file_get(file_name)

    def file_copy_at(self, timestamp: int, file_from: str, file_to: str):
        self._on_ttl_event(timestamp)
        self.file_copy(source=file_from, dest=file_to)
        copied_file = self.file_system[file_to]
        copied_file.set_created_at(timestamp)

    def file_search_at(self, timestamp: int, prefix: str) -> list[str]:
        self._on_ttl_event(timestamp)
        return self.file_search(prefix)

    # TODO:
    def rollback(self, timestamp: int):
        pass

    def _on_ttl_event(self, timestamp: int):
        while len(self.ttl_files_list) > 0 and self.ttl_files_list[0] <= timestamp:
            expired_file = heapq.heappop(self.ttl_files_list)[1]
            self._delete_file(file_name=expired_file.file_name)

    def _delete_file(self, file_name: str):
        if not self._file_exist(file_name):
            return
        del self.file_system[file_name]

    def _file_exist(self, file_name: str) -> bool:
        return file_name in self.file_system


#
