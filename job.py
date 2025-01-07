from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import logging
from logging.handlers import QueueHandler
import random
from time import sleep
from uuid import UUID

log = logging.getLogger(__name__)


class JobException(Exception):
    pass


class JobStatus(Enum):
    PENDING = 0
    COMPLETED = 1
    FAILED = 2


@dataclass
class Job:
    id: int
    dependencies: list[Job]
    status: JobStatus = field(default=JobStatus.PENDING, init=False)
    exception: Exception | None = field(default=None, init=False)

    def run(self, queue=None):
        try:
            if queue:
                global log
                log = logging.getLogger()
                log.addHandler(QueueHandler(queue))
                log.setLevel(logging.INFO)
            # We simulate that some random amount of work is being done.
            log.info(f"Job {self.id} is running...")
            for i in range(random.randint(1, 5)):
                log.info(f"Job {self.id} is running... {i}")
                # We simulate that the job has a 10% chance of failing.
                if random.random() < 0.3:
                    raise JobException(f"Job {self.id} failed.")
                sleep(random.random() * 2)

            log.info(f"Job {self.id} completed.")
            self.status = JobStatus.COMPLETED

            return self
        except JobException as e:
            log.exception(f"Job {self.id} failed with exception: {e}", exc_info=(type(e), e, e.__traceback__))
            self.status = JobStatus.FAILED
            self.exception = e
            return self

    def __str__(self):
        return f"Job {self.id} ({self.status.name})"
