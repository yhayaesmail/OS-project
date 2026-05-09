from process import Process
from priority_scheduler import priority_scheduler
from srtf_scheduler import srtf_scheduler
from metrics import calculate_metrics
from gantt import print_gantt
from input_validator import InputValidator



def print_results(processes, algo_name):
    print(f"\n=== {algo_name} Results ===")
    print(f"{'PID':<5} {'WT':<8} {'TAT':<8} {'RT':<8}")
    print("-" * 30)
    for p in processes:
        print(f"{p.pid:<5} {p.waiting_time:<8} {p.turnaround_time:<8} {p.response_time:<8}")
    avg_wt, avg_tat, avg_rt = calculate_metrics(processes)
    print(f"\nAverage WT: {avg_wt:.2f}")
    print(f"Average TAT: {avg_tat:.2f}")
    print(f"Average RT: {avg_rt:.2f}")

def waiting_spread(processes):
    values = [p.waiting_time for p in processes]
    return max(values) - min(values) if values else 0

def print_comparison_summary(pri_proc, srtf_proc):
    pri_avg_wt, pri_avg_tat, pri_avg_rt = calculate_metrics(pri_proc)
    srtf_avg_wt, srtf_avg_tat, srtf_avg_rt = calculate_metrics(srtf_proc)

    print(f"Priority -> Avg WT: {pri_avg_wt:.2f}, Avg TAT: {pri_avg_tat:.2f}, Avg RT: {pri_avg_rt:.2f}")
    print(f"SRTF     -> Avg WT: {srtf_avg_wt:.2f}, Avg TAT: {srtf_avg_tat:.2f}, Avg RT: {srtf_avg_rt:.2f}")

    print("\nAnalysis Questions:")
    if pri_avg_wt < srtf_avg_wt:
        print("- Priority produced the lower average waiting time.")
    elif srtf_avg_wt < pri_avg_wt:
        print("- SRTF produced the lower average waiting time.")
    else:
        print("- Both algorithms produced the same average waiting time.")

    if pri_avg_rt < srtf_avg_rt:
        print("- Priority produced the lower average response time.")
    elif srtf_avg_rt < pri_avg_rt:
        print("- SRTF produced the lower average response time.")
    else:
        print("- Both algorithms produced the same average response time.")

    print("- Priority values improve urgent-process treatment when urgent processes have the best priority values.")
    print("- SRTF favors short remaining jobs aggressively and may delay longer jobs.")

    pri_spread = waiting_spread(pri_proc)
    srtf_spread = waiting_spread(srtf_proc)
    if pri_spread < srtf_spread:
        fairer = "Priority appeared fairer by waiting-time spread."
    elif srtf_spread < pri_spread:
        fairer = "SRTF appeared fairer by waiting-time spread."
    else:
        fairer = "Both algorithms appeared equally fair by waiting-time spread."

    print("\nFinal Conclusion:")
    if pri_avg_wt < srtf_avg_wt:
        print("- Priority performed better on average waiting time for this dataset.")
    elif srtf_avg_wt < pri_avg_wt:
        print("- SRTF performed better on average waiting time for this dataset.")
    else:
        print("- Both algorithms tied on average waiting time for this dataset.")
    print(f"- Metrics trade-off: WT {pri_avg_wt:.2f} vs {srtf_avg_wt:.2f}, "
          f"TAT {pri_avg_tat:.2f} vs {srtf_avg_tat:.2f}, RT {pri_avg_rt:.2f} vs {srtf_avg_rt:.2f}.")
    print("- Main trade-off: Priority follows urgency policy; SRTF optimizes short remaining work.")
    print(f"- {fairer}")

def main():
    print("="*50)
    print("Priority (preemptive) vs SRTF Comparison")
    print("="*50)

    n = InputValidator.get_process_count("Enter number of processes: ")
    processes = []
    existing_ids = []

    for i in range(n):
        print(f"\n--- Process {i+1} ---")
        pid = InputValidator.get_pid("Process ID: ", existing_ids)
        arrival = InputValidator.get_positive_int("Arrival Time: ")
        burst = InputValidator.get_burst("Burst Time: ")
        priority = InputValidator.get_priority("Priority (1=highest, 1-10): ")

        existing_ids.append(pid)
        processes.append(Process(pid, arrival, burst, priority))

    print("\n" + "="*50)
    print("Priority Scheduler (Preemptive)")
    print("="*50)
    pri_proc, pri_gantt = priority_scheduler(processes)
    print_gantt(pri_gantt, "Priority")
    print_results(pri_proc, "Priority")

    print("\n" + "="*50)
    print("SRTF Scheduler")
    print("="*50)
    srtf_proc, srtf_gantt = srtf_scheduler(processes)
    print_gantt(srtf_gantt, "SRTF")
    print_results(srtf_proc, "SRTF")

    print("\n" + "="*50)
    print("Comparison Summary")
    print("="*50)
    print_comparison_summary(pri_proc, srtf_proc)


if __name__ == "__main__":
    main()
