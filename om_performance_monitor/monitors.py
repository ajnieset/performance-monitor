# from decimal import Decimal
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from exceptions import SaveError, TimerError


@dataclass
class PerformanceMonitor:
    """
    Custom Performance Monitor to measure and log function performance.

    __enter__ -> start timer in a context manager
    __exit__  -> ends and logs time when context ends

    Call `start` to start timer for a block
    Call `end` to end timer for the most recently started block
    """

    start_time: Optional[float] = field(default=None, init=False, repr=False)
    end_time: Optional[float] = field(default=None, init=False, repr=False)
    timer_blocks: dict = field(default_factory=dict)
    logger: Optional[Callable[[str], None]] = print

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc_info):
        self.end()
        self.save_block("ctx_manager")
        self.log_time("ctx_manager")

    def start(self) -> None:
        """
        Start timer. if timer is running it will reset the timer
        """
        self.start_time = time.perf_counter()

    def end(self) -> None:
        """
        Stop timer. if there is no start time raise error
        """
        if self.start_time is None:
            raise TimerError(
                "Timer was not started. Call Timer.start() to begin the timer\n"
            )

        self.end_time = time.perf_counter()

    def reset(self, clear_blocks: bool = False) -> None:
        """
        Reset the monitor to clear timer in progress.

        `clear_blocks` Flag to reset saved blocks. DEFAULT False
        """
        self.start_time = None
        self.end_time = None

        if clear_blocks:
            self.timer_blocks = {}

    def save_block(self, block_name: str) -> None:
        """
        Save the timer results to blocks. Resets the times to
        """
        try:
            elapsed = float(self.end_time) - float(self.start_time)
            self.timer_blocks.update(
                {
                    block_name: {
                        "start_time": self.start_time,
                        "end_time": self.end_time,
                        "elapsed": elapsed,
                    }
                }
            )
        except Exception as e:
            raise SaveError(f"Error saving timer block. Error: {e}\n")

    def log_time(self, block_name: str) -> None:
        """
        Save block to Monitor
        """
        try:
            timer_block = self.timer_blocks[block_name]
        except Exception:
            raise TimerError(
                "No saved timer blocks. Call Timer.save_block() to save a timer block or start/end a timer and save it"
            )

        if self.logger is None:
            raise TimerError("No logger configured with the timer")

        self.logger(
            f"{block_name} timer | start time: {timer_block['start_time']} | end time: {timer_block['end_time']} | elapsed: {timer_block['elapsed']}"
        )
