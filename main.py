import logging
from multiprocessing import Manager, Pool, Process
from multiprocessing.pool import AsyncResult
import random
import signal
import sys
from time import sleep
from typing import Callable
from uuid import uuid4

from rich.logging import RichHandler
from job import Job, JobStatus

log = logging.getLogger(__name__)


def init_logging():
    log = logging.getLogger("Daemon Logger")
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)],
    )
    return log


def listener_process(setup_logging: Callable, queue):
    log = setup_logging()
    log.info("Listener started.")
    while True:
        try:
            record = queue.get()
            if record is None:
                break
            log.handle(record)
        except KeyboardInterrupt:
            log.info("Listener stopped.")
            break
        except Exception:
            log.error("Failure in listener_process")


def callback(job: Job):
    match job.status:
        case JobStatus.COMPLETED:
            log.info(f"Job {job.id} completed.")
        case JobStatus.FAILED:
            e = job.exception
            log.exception(f"Job {job.id} failed with exception: {e}", exc_info=e)
        case JobStatus.PENDING:
            log.info(f"Job {job.id} is still pending.")
        case _:
            log.info(f"Job {job.id} is in an unknown state.")


def run_daemon(queue):
    log.info("Daemon started.")
    njobs = 0
    while True:
        try:
            # Simulate that we look for jobs
            jobs = []
            for _ in range(random.randint(0, 3)):
                njobs += 1
                jobs.append(Job(id=njobs, dependencies=[]))
                sleep(0.5)
            if not jobs:
                log.info("No jobs found. Sleeping...")
                sleep(1)
                continue
            with Pool(3, initializer=signal.signal, initargs=(signal.SIGINT, signal.SIG_IGN)) as pool:
                aos = []
                while jobs:
                    job = jobs.pop(0)
                    log.info(f"Submitting job {job.id}...")
                    try:
                        ao = pool.apply_async(
                            job.run,
                            args=(queue,),
                            callback=callback,
                        )
                        aos.append(ao)
                    except KeyboardInterrupt:
                        log.info("Cancelled.")

                for ao in aos:
                    ao.wait()
                    # print(ao.get())

            sleep(1)
        except KeyboardInterrupt:
            log.info("Daemon stopped.")
            break


def main():
    log = init_logging()
    log.info("Main started.")
    try:
        raise ValueError("This is a test exception.")
    except ValueError as e:
        log.exception("Exception occurred.")
    manager = Manager()
    queue = manager.Queue()
    listener = Process(
        target=listener_process,
        args=(
            init_logging,
            queue,
        ),
    )
    listener.start()

    run_daemon(queue)

    queue.put_nowait(None)
    listener.join()
    log.info("Main stopped.")


if __name__ == "__main__":
    main()
