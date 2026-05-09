class Process:
    def __init__(self, pid, arrival, burst, priority, order=0):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.priority = priority
        self.order = order
        self.remaining = burst
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = -1
