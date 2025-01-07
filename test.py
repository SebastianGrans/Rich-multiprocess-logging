


#%%
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


def catch_exceptions(func):
    def wrapper(self, queue=None):
        try:
            return func(self, queue)
        except Exception as e:
            self.status = JobStatus.FAILED
            self.exception = e
            log.error(f"Job {self.id} failed with exception: {e}")
            return self

    return wrapper


@dataclass
class Job:
    id: int
    dependencies: list[Job]
    status: JobStatus = field(default=JobStatus.PENDING, init=False)
    exception: Exception | None = field(default=None, init=False)

    @catch_exceptions
    def run(self, queue=None):
        if queue:
            self.asdf = 5
        else:
            self.asdf = 6
        for i in range(random.randint(1, 5)):
            log.info(f"Job {self.id} is running... {i}")
            # We simulate that the job has a 10% chance of failing.
            raise JobException(f"Job {self.id} failed.")
            sleep(random.random() * 2)

        log.info(f"Job {self.id} completed.")
        self.status = JobStatus.COMPLETED

        return self

#%%
log.setLevel(logging.INFO)
j = Job(1, []).run()
# %%

from rich.traceback import Traceback
from rich.