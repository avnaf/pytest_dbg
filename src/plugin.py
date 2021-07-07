import logging
import pytest
import threading
import time

from contextlib import suppress
from importlib import import_module
from pynput.keyboard import Key, Controller


_logger = logging.getLogger()


class Debugger:
    SupportedDebuggers = (
        'ipdb',
        'pdb',
        'pudb',
    )
    def __init__(self, debugger):
        self._debugger = debugger
        self._in_debugger_event = threading.Event()
        if debugger not in self.SupportedDebuggers:
            raise AttributeError(f'supported debuggers are: {self.SupportedDebuggers}')

    def _continue_until_func_start(self):
        # wait to the event that will be set just before dropping into debugger
        while not self._in_debugger_event.is_set():
            time.sleep(0.1)

        keyboard = Controller()

        # skip the set_trace line
        keyboard.press('n')
        keyboard.release('n')
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

        # step into the failed function
        keyboard.press('s')
        keyboard.release('s')
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

    def set_trace(self):
        drop_into_correct_line = threading.Thread(target=self._continue_until_func_start)
        drop_into_correct_line.start()

        module = import_module(self._debugger)
        self._in_debugger_event.set()
        getattr(module, 'set_trace')()


def pytest_exception_interact(node, call, report):
    debugger = node.config.getoption('--dbg')
    if not debugger:
        return

    failed_func = node.function

    _logger.info(f'Exception detected on {failed_func}. Dropping into debugger...')

    with suppress(Exception):
        Debugger(debugger).set_trace()
        failed_func()

    _logger.info(f'Continuing regular execution...')


def pytest_addoption(parser):
    group = parser.getgroup('test session debugging and configuration')
    group.addoption(
        '--dbg',
        default=None,
        choices=Debugger.SupportedDebuggers,
        help='re-run failed test and drop into a debugger at the start of the test',
    )
