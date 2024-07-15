from multiprocessing import Queue, Manager, Pool, Process

from rich.logging import RichHandler


def listener_process(queue):
    pass


def run_daemon():

    while True:
        pass


def main():
    manager = Manager()
    queue = manager.Queue()
    listener = Process(target=listener_process, args=(queue,))

    run_daemon()

    queue.put_nowait(None)


if __name__ == "__main__":
    main()
