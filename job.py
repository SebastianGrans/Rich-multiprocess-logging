from __future__ import annotations
from enum import Enum
import random
from time import sleep
from uuid import UUID, uuid4


class JobStatus(Enum):
    PENDING = 0
    COMPLETED = 1
    FAILED = 2


class Job:
    id: UUID
    status: JobStatus
    dependencies: list[Job]

    def run(self):
        # We simulate that some random amount of work is being done.
        for i in range(random.randint(1, 5)):
            print(f"Job {self.id} is running... {i}")
            # We simulate that the job has a 10% chance of failing.
            if random.random() < 0.1:
                self.status = JobStatus.FAILED
                print(f"Job {self.id} failed.")
                return
            sleep(1)

        self.status = JobStatus.COMPLETED

    def __str__(self):
        return f"Job {self.id} ({self.status.name})"
