from process import Process

def priority_scheduler(processes):
    processes = [
        Process(p.pid, p.arrival, p.burst, p.priority, index)
        for index, p in enumerate(processes)
    ]
    processes.sort(key=lambda x: (x.arrival, x.order))

    time = 0
    completed = 0
    n = len(processes)
    ready_queue = []
    gantt = []
    current_process = None
    current_start = 0

    while completed < n:
        for p in processes:
            if p.arrival == time and p.remaining > 0:
                ready_queue.append(p)

        if current_process is not None and current_process.remaining == 0:
            current_process.completion_time = time
            completed += 1
            current_process = None

        if current_process is not None and ready_queue:
            ready_queue.sort(key=lambda x: (x.priority, x.arrival, x.order))
            if (ready_queue[0].priority, ready_queue[0].arrival, ready_queue[0].order) < \
               (current_process.priority, current_process.arrival, current_process.order):
                ready_queue.append(current_process)
                current_process = None

        if current_process is None and ready_queue:
            ready_queue.sort(key=lambda x: (x.priority, x.arrival, x.order))
            current_process = ready_queue.pop(0)
            current_start = time
            if current_process.response_time == -1:
                current_process.response_time = time - current_process.arrival

        if current_process is not None:
            current_process.remaining -= 1
            time += 1
        else:
            time += 1

        if current_process is not None:
            if len(gantt) == 0 or gantt[-1][0] != current_process.pid:
                gantt.append([current_process.pid, current_start, time])
            else:
                gantt[-1][2] = time

    for p in processes:
        p.turnaround_time = p.completion_time - p.arrival
        p.waiting_time = p.turnaround_time - p.burst

    return processes, gantt
