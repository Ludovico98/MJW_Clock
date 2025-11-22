from time import sleep

try:
    import RPi.GPIO as GPIO
except ImportError as exc:
    raise SystemExit("RPi.GPIO library is required to control the MJW clock.") from exc


class ClockController:
    """Low-level controller for the MJW clock stepper motors."""

    STEP_MIN = 31
    STEP_HR = 37
    ENA_MIN = 29
    ENA_HR = 35
    DIR_MIN = 40
    DIR_HR = 33
    SWITCH_MIN = 32
    SWITCH_HR = 22

    FAST_DELAY = 0.001

    MINUTE_STEPS_PER_MINUTE = 1238
    HOUR_STEPS_PER_MINUTE = 100

    MIN_RELEASE_STEPS = 2000
    HOUR_RELEASE_STEPS = 1000
    MIN_SWITCH_WINDOW_STEPS = 600
    HOUR_SWITCH_WINDOW_STEPS = 400

    def __init__(self) -> None:
        self._initialised = False

    def __enter__(self) -> "ClockController":
        self.initialise()
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        self.cleanup()

    # Public API -----------------------------------------------------------------
    def initialise(self) -> None:
        if self._initialised:
            return

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        GPIO.setup(self.STEP_MIN, GPIO.OUT)
        GPIO.setup(self.STEP_HR, GPIO.OUT)
        GPIO.setup(self.ENA_MIN, GPIO.OUT)
        GPIO.setup(self.ENA_HR, GPIO.OUT)
        GPIO.setup(self.DIR_MIN, GPIO.OUT)
        GPIO.setup(self.DIR_HR, GPIO.OUT)
        GPIO.setup(self.SWITCH_MIN, GPIO.IN)
        GPIO.setup(self.SWITCH_HR, GPIO.IN)

        # Disable motors until they are needed
        GPIO.output(self.ENA_MIN, GPIO.HIGH)
        GPIO.output(self.ENA_HR, GPIO.HIGH)
        GPIO.output(self.DIR_MIN, GPIO.HIGH)
        GPIO.output(self.DIR_HR, GPIO.HIGH)

        self._initialised = True

    def cleanup(self) -> None:
        if not self._initialised:
            return

        try:
            GPIO.output(self.ENA_MIN, GPIO.HIGH)
            GPIO.output(self.ENA_HR, GPIO.HIGH)
        except RuntimeError:
            # GPIO might already be cleaned up if something went wrong.
            pass
        GPIO.cleanup()
        self._initialised = False

    def set_hour(self, hour_index: int, minute_offset: int = 0) -> None:
        hour_index %= 12
        minute_offset = max(0, min(59, minute_offset))

        self._home_hour()

        steps_for_hour = hour_index * self._hour_steps_per_hour
        steps_for_fraction = int(round((minute_offset / 60.0) * self._hour_steps_per_hour))
        total_steps = (steps_for_hour + steps_for_fraction) % self._hour_steps_per_rev

        self._run_hour_steps(total_steps)

    def set_minute(self, minute_value: int) -> None:
        minute_value = max(0, min(59, minute_value))

        self._home_minute()

        total_steps = minute_value * self.MINUTE_STEPS_PER_MINUTE
        self._run_minute_steps(total_steps)

    # Internal helpers -----------------------------------------------------------
    @property
    def _hour_steps_per_hour(self) -> int:
        return self.HOUR_STEPS_PER_MINUTE * 60

    @property
    def _hour_steps_per_rev(self) -> int:
        return self._hour_steps_per_hour * 12

    @property
    def _minute_steps_per_rev(self) -> int:
        return self.MINUTE_STEPS_PER_MINUTE * 60

    def _minute_step(self) -> None:
        GPIO.output(self.STEP_MIN, GPIO.HIGH)
        sleep(self.FAST_DELAY)
        GPIO.output(self.STEP_MIN, GPIO.LOW)
        sleep(self.FAST_DELAY)

    def _hour_step(self) -> None:
        GPIO.output(self.STEP_HR, GPIO.HIGH)
        sleep(self.FAST_DELAY)
        GPIO.output(self.STEP_HR, GPIO.LOW)
        sleep(self.FAST_DELAY)

    def _home_minute(self) -> None:
        self._enable_minute()
        self._release_minute_if_pressed()

        GPIO.output(self.DIR_MIN, GPIO.HIGH)
        steps = 0
        while GPIO.input(self.SWITCH_MIN) == GPIO.HIGH:
            if steps > self._minute_steps_per_rev:
                raise RuntimeError("Minute home switch not detected within one revolution")
            self._minute_step()
            steps += 1
        window = 0
        while GPIO.input(self.SWITCH_MIN) == GPIO.LOW and window < self.MIN_SWITCH_WINDOW_STEPS:
            self._minute_step()
            window += 1
        if window:
            GPIO.output(self.DIR_MIN, GPIO.LOW)
            backtrack = window // 2
            for _ in range(backtrack):
                self._minute_step()
            GPIO.output(self.DIR_MIN, GPIO.HIGH)
        self._disable_minute()

    def _home_hour(self) -> None:
        self._enable_hour()
        self._release_hour_if_pressed()

        GPIO.output(self.DIR_HR, GPIO.HIGH)
        steps = 0
        while GPIO.input(self.SWITCH_HR) == GPIO.HIGH:
            if steps > self._hour_steps_per_rev:
                raise RuntimeError("Hour home switch not detected within one revolution")
            self._hour_step()
            steps += 1
        window = 0
        while GPIO.input(self.SWITCH_HR) == GPIO.LOW and window < self.HOUR_SWITCH_WINDOW_STEPS:
            self._hour_step()
            window += 1
        if window:
            GPIO.output(self.DIR_HR, GPIO.LOW)
            backtrack = window // 2
            for _ in range(backtrack):
                self._hour_step()
            GPIO.output(self.DIR_HR, GPIO.HIGH)
        self._disable_hour()

    def _run_minute_steps(self, steps: int) -> None:
        if steps <= 0:
            return
        self._enable_minute()
        GPIO.output(self.DIR_MIN, GPIO.HIGH)
        for _ in range(steps):
            self._minute_step()
        self._disable_minute()

    def _run_hour_steps(self, steps: int) -> None:
        if steps <= 0:
            return
        self._enable_hour()
        GPIO.output(self.DIR_HR, GPIO.HIGH)
        for _ in range(steps):
            self._hour_step()
        self._disable_hour()

    def _release_minute_if_pressed(self) -> None:
        if GPIO.input(self.SWITCH_MIN) == GPIO.LOW:
            GPIO.output(self.DIR_MIN, GPIO.LOW)
            steps = 0
            while GPIO.input(self.SWITCH_MIN) == GPIO.LOW:
                if steps > self.MIN_RELEASE_STEPS:
                    raise RuntimeError("Minute switch stuck while backing off")
                self._minute_step()
                steps += 1
        GPIO.output(self.DIR_MIN, GPIO.HIGH)

    def _release_hour_if_pressed(self) -> None:
        if GPIO.input(self.SWITCH_HR) == GPIO.LOW:
            GPIO.output(self.DIR_HR, GPIO.LOW)
            steps = 0
            while GPIO.input(self.SWITCH_HR) == GPIO.LOW:
                if steps > self.HOUR_RELEASE_STEPS:
                    raise RuntimeError("Hour switch stuck while backing off")
                self._hour_step()
                steps += 1
        GPIO.output(self.DIR_HR, GPIO.HIGH)

    def _enable_minute(self) -> None:
        GPIO.output(self.ENA_MIN, GPIO.LOW)

    def _disable_minute(self) -> None:
        GPIO.output(self.ENA_MIN, GPIO.HIGH)

    def _enable_hour(self) -> None:
        GPIO.output(self.ENA_HR, GPIO.LOW)

    def _disable_hour(self) -> None:
        GPIO.output(self.ENA_HR, GPIO.HIGH)


__all__ = ["ClockController"]
