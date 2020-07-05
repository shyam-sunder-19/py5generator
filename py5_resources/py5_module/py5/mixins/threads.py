import sys
import time
import threading
from collections.abc import Iterable
from typing import Callable, Dict, Tuple

from .. import methods


class Py5Thread:

    def __init__(self, sketch, f, args, kwargs):
        self.sketch = sketch
        self.f = f
        self.args = args
        self.kwargs = kwargs

    def stop(self):
        pass

    def __call__(self):
        try:
            self.f(*self.args, **self.kwargs)
        except Exception:
            methods.handle_exception(*sys.exc_info())
            self.sketch._terminate_sketch()


class Py5Repeater(Py5Thread):

    def __init__(self, sketch, f, delay, args, kwargs):
        super().__init__(sketch, f, args, kwargs)
        self.repeat = True
        self.delay = delay
        self.e = threading.Event()

    def stop(self):
        super().stop()
        self.repeat = False
        self.e.set()

    def __call__(self):
        try:
            while self.repeat:
                start_time = time.time()
                self.f(*self.args, **self.kwargs)
                self.e.wait(max(0, start_time + self.delay - time.time()))
        except Exception:
            self.stop()
            methods.handle_exception(*sys.exc_info())
            self.sketch._terminate_sketch()


class ThreadsMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._py5threads = {}

    # *** BEGIN METHODS ***

    def _check_param_types(self, args, kwargs):
        if not isinstance(args, Iterable) and args is not None:
            raise RuntimeError('args argument must be iterable (such as a tuple or list)')
        if not isinstance(kwargs, dict) and kwargs is not None:
            raise RuntimeError('kwargs argument must be a dictionary')

        kwargs = kwargs or {}
        args = args or ()

        return args, kwargs

    def _launch_py5thread(self, name, py5thread):
        if isinstance(py5thread, Py5Repeater) and self.has_thread(name):
            self.stop_thread(name, wait=True)

        t = threading.Thread(target=py5thread, name=name)
        t.start()
        self._py5threads[t.name] = (t, py5thread)

        return t.name

    def launch_thread(self, f: Callable, name: str = None,
                      args: Tuple = None, kwargs: Dict = None) -> str:
        """$class_launch_thread"""
        args, kwargs = self._check_param_types(args, kwargs)
        return self._launch_py5thread(name, Py5Thread(self, f, args, kwargs))

    def launch_repeating_thread(self, f: Callable, name: str = None, time_delay: float = 0,
                                args: Tuple = None, kwargs: Dict = None) -> str:
        """$class_launch_repeating_thread"""
        args, kwargs = self._check_param_types(args, kwargs)
        return self._launch_py5thread(name, Py5Repeater(self, f, time_delay, args, kwargs))

    def _remove_dead_threads(self):
        thread_names = list(self._py5threads.keys())
        for t_name in thread_names:
            if not self._py5threads[t_name][0].is_alive():
                del self._py5threads[t_name]

    def has_thread(self, name: str) -> None:
        """$class_has_thread"""
        self._remove_dead_threads()
        return name in self._py5threads

    def stop_thread(self, name: str, wait: bool = False) -> None:
        """$class_stop_thread"""
        if name in self._py5threads:
            t, py5thread = self._py5threads[name]
            py5thread.stop()
            if wait:
                t.join()
            del self._py5threads[name]

    def stop_all_threads(self, wait: bool = False) -> None:
        """$class_stop_all_threads"""
        current_thread_name = threading.current_thread().name
        for name in self.list_threads():
            if name == current_thread_name:
                # don't try to join a thread with itself
                continue
            self.stop_thread(name, wait=wait)

    def list_threads(self) -> None:
        """$class_list_threads"""
        self._remove_dead_threads()
        return list(self._py5threads.keys())

    def _shutdown(self):
        self.stop_all_threads(wait=True)
        super()._shutdown()
