import time
from datetime import datetime
import numpy as np
from PyQt5.QtCore import QTimer, QObject, pyqtSignal, pyqtSlot

class DataSimulator(QObject):
    data_generated = pyqtSignal(float, tuple)

    def __init__(self, interval=1.0):
        super().__init__()
        self.interval = interval  # Interval in seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.generate_data)

    def start(self):
        self.timer.start(self.interval * 1000)  # Convert interval to milliseconds

    def stop(self):
        self.timer.stop()

    def generate_data(self):
        # Simulate current time (Unix time)
        current_time = time.time()

        # Simulate temperatures (replace with your actual data generation logic)
        temperatures = tuple(np.random.uniform(20.0, 30.0, size=8))

        # Emit signal with simulated data
        self.data_generated.emit(current_time, temperatures)
