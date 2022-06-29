from threading import Timer


class RestartableTimer:
    def __init__(self, interval, function, args=None, kwargs=None):
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.interval = interval
        self.function = function
        self.timer = Timer(self.interval, self.function, args=self.args, kwargs=self.kwargs)

    def restart(self):
        self.start()

    def start(self):
        self.timer.cancel()
        self.timer = Timer(self.interval, self.function, args=self.args, kwargs=self.kwargs)
        self.timer.start()

    def cancel(self):
        self.timer.cancel()
