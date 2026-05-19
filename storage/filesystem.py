import heapq

NO_TTL = 0
NO_CREATED_AT = -1


class File:
    def __init__(self, file_name: str, size: int):
        self.file_name = file_name
        self.size = size
        self.ttl = NO_TTL
        self.created_at = NO_CREATED_AT

    def copy(self, file_name: str) -> "File":
        file = File(file_name=file_name, size=self.size)
        file.set_ttl(self.ttl)
        file.set_created_at(self.created_at)
        return file

    def set_ttl(self, ttl: int):
        self.ttl = ttl

    def set_created_at(self, created_at: int):
        self.created_at = created_at

    def __str__(self):
        return f"{self.file_name}({self.size})"

    def __repr__(self):
        return f"File(file_name={self.file_name}, size={self.size})"


class FileSystem:
    def __init__(self):
        self.file_system: dict[str, File] = {}
        self.ttl_files_list: list[tuple[int, str, File]] = []

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
        self.file_system[dest] = existing_file.copy(dest)

    def file_search(self, prefix: str) -> list[str]:
        result: list[File] = []
        for file_name, file in self.file_system.items():
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
        file = self.file_system[file_name]
        if ttl is not None:
            expiry = timestamp + ttl
            file.set_ttl(ttl)
            self._add_to_ttl_list(file=file, expiry=expiry)
        file.set_created_at(timestamp)

    def file_get_at(self, timestamp: int, file_name: str) -> int | None:
        self._on_ttl_event(timestamp)
        return self.file_get(file_name)

    def file_copy_at(self, timestamp: int, file_from: str, file_to: str):
        self._on_ttl_event(timestamp)
        self.file_copy(source=file_from, dest=file_to)
        copied_file = self.file_system[file_to]
        copied_file.set_created_at(timestamp)
        if copied_file.ttl == NO_TTL:
            return
        expiry = copied_file.ttl + copied_file.created_at
        self._add_to_ttl_list(file=copied_file, expiry=expiry)

    def file_search_at(self, timestamp: int, prefix: str) -> list[str]:
        self._on_ttl_event(timestamp)
        return self.file_search(prefix)

    # TODO:
    def rollback(self, timestamp: int):
        # delete files in fs where created > ts i.e. files created after this ts
        self.ttl_files_list = []  # need to recalculate the ttl
        files_to_delete: list[str] = []
        for key, file in self.file_system.items():
            print("checking file", file, "created at", file.created_at)
            if file.created_at <= timestamp:
                continue
            files_to_delete.append(key)
        for file_name in files_to_delete:
            self._delete_file(file_name)
            if file.ttl == NO_TTL:
                continue
            expiry = file.ttl + file.created_at
            self._add_to_ttl_list(file=file, expiry=expiry)
        heapq.heapify(self.ttl_files_list)
        self._on_ttl_event(timestamp)

    def _add_to_ttl_list(self, file: File, expiry: int):
        self.ttl_files_list.append((expiry, file.file_name, file))

    def _on_ttl_event(self, timestamp: int):
        while len(self.ttl_files_list) > 0 and self.ttl_files_list[0][0] <= timestamp:
            expired_file_name = heapq.heappop(self.ttl_files_list)[1]
            self._delete_file(file_name=expired_file_name)

    def _delete_file(self, file_name: str):
        if not self._file_exist(file_name):
            return
        del self.file_system[file_name]

    def _file_exist(self, file_name: str) -> bool:
        return file_name in self.file_system


#
