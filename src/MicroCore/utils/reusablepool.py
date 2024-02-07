from queue import Queue, Empty
import threading
from contextlib import contextmanager

class ReusablePool:
    """
    Manage Reusable objects for use by microservice.
    """

    def __init__(self, size, reusable_factory):
        self._reusables = Queue(maxsize=size)
        for _ in range(size):
            reusable_item = reusable_factory()
            self._reusables.put(reusable_item)
        self._lock = threading.Lock()

    def acquire(self):
        with self._lock:
            try:
                return self._reusables.get_nowait()
            except Empty:
                raise IndexError("No reusable objects available in the pool.")

    def release(self, reusable):
        with self._lock:
            self._reusables.put(reusable)

    @contextmanager
    def auto_release(self):
        resource = self.acquire()
        try:
            yield resource
        finally:
            self.release(resource)

