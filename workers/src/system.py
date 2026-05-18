from src.worker import Worker


class WorkerSystem:
    def __init__(self):
        self.workers_database: dict[str, Worker] = {}

    def add_worker(self, worker_id: str, position: str, compensation: int) -> str:
        """
        add the workerId to the system and save additional information about them: their position and compensation.
        """
        if self._get_worker(worker_id) is not None:
            return "false"
        new_worker = Worker(
            worker_id=worker_id, position=position, compensation=compensation
        )
        self.workers_database[worker_id] = new_worker
        return "true"

    def register(self, worker_id: str, timestamp: int) -> str:
        """
        register the time when the workerId entered or left the office. The time is represented by the timestamp
        """
        worker = self._get_worker(worker_id)
        if worker is None:
            return "invalid_request"
        worker.register(timestamp=timestamp)
        return "registered"

    def get(self, worker_id: str) -> str:
        """
        returns a string representing the total calculated amount of time that the workerId spent in the office
        """
        worker = self._get_worker(worker_id)
        if worker is None:
            return ""
        return str(worker.get_total_working_hours())

    def _get_worker(self, worker_id: str) -> Worker | None:
        """gets a worker by id or none"""
        return (
            self.workers_database[worker_id]
            if worker_id in self.workers_database
            else None
        )

    def top_n_workers(self, n: int, position: str) -> str:
        """
        returns the string representing ids of the top n workers with the given position sorted in descending order by the total time spent in the office.
        """
        filtered_workers = [
            worker
            for worker in self.workers_database.values()
            if worker.position == position
        ]
        if len(filtered_workers) == 0:
            return ""
        sorted_workers = sorted(
            filtered_workers,
            key=lambda worker: (-worker.get_total_working_hours(), worker.worker_id),
        )[:n]
        result = [
            f"{worker.worker_id}({worker.get_total_working_hours()})"
            for worker in sorted_workers
        ]
        return ", ".join(result)

    def promote(
        self,
        worker_id: str,
        new_position: str,
        new_compensation: str,
        start_timestamp: str,
    ) -> str:
        pass
