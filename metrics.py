def calculate_metrics(processes):
    total_wt = 0
    total_tat = 0
    total_rt = 0
    n = len(processes)

    # waiting_time = turnaround_time - burst_time
    # turnaround_time = completion_time - arrival_time
    # response_time = first_cpu_start_time - arrival_time

    for p in processes:
        total_wt += p.waiting_time
        total_tat += p.turnaround_time
        total_rt += p.response_time

    avg_wt = total_wt / n
    avg_tat = total_tat / n
    avg_rt = total_rt / n

    return avg_wt, avg_tat, avg_rt