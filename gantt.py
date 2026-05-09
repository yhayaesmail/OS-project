def print_gantt(gantt, algorithm_name):
    print(f"\n{algorithm_name} Execution Order:")
    print("Time\t| Running Process")
    print("-" * 25)

    for item in gantt:
        pid, start, end = item
        print(f"{start}-{end}\t| {pid}")