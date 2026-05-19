from typing import Literal, get_args

OfficeStatus = Literal["in-office", "out-of-office"]

STATUS_IN_OFFICE: str = get_args(OfficeStatus)[0]
STATUS_OUT_OFFICE: str = get_args(OfficeStatus)[1]


class StatusHistory:
    def __init__(
        self, worker_id: str, status: OfficeStatus, timestamp: int, position: str
    ):
        self.worker_id = worker_id
        self.status = status
        self.timestamp = timestamp
        self.position = position
        self.total_duration = 0


class Worker:
    def __init__(self, worker_id: str, position: str, compensation: int):
        self.worker_id = worker_id
        self.position = position
        self.compensation = compensation
        self.status = STATUS_OUT_OFFICE
        self.status_history: list[StatusHistory] = []
        self.total_working_hours = 0

    def register(self, timestamp: int):
        self.status = (
            STATUS_OUT_OFFICE if self.status == STATUS_IN_OFFICE else STATUS_IN_OFFICE
        )
        self.add_to_history(timestamp=timestamp)
        if self.status == STATUS_OUT_OFFICE:
            self.calculate_last_working_hours()

    def add_to_history(self, timestamp: int):
        history = StatusHistory(
            worker_id=self.worker_id,
            status=self.status,
            timestamp=timestamp,
            position=self.position,
        )
        self.status_history.append(history)

    def calculate_last_working_hours(self):
        if len(self.status_history) < 2:
            return
        self.total_working_hours += (
            self.status_history[-1].timestamp - self.status_history[-2].timestamp
        )

    def get_total_working_hours(self) -> int:
        return self.total_working_hours