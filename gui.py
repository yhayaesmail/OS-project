import tkinter as tk
from tkinter import ttk, messagebox

from process import Process
from priority_scheduler import priority_scheduler
from srtf_scheduler import srtf_scheduler
from metrics import calculate_metrics


class SchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Priority vs SRTF Comparison Tool")
        self.root.geometry("1200x900")
        self.root.minsize(1000, 650)

        self.processes_list = []

        self.setup_style()
        self.build_main_layout()
        self.setup_ui()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Title.TLabel", font=("Arial", 16, "bold"), foreground="#2c3e50")
        style.configure("Info.TLabel", font=("Arial", 10), foreground="#34495e")
        style.configure("Section.TLabelframe.Label", font=("Arial", 10, "bold"))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", rowheight=24, font=("Arial", 10))
        style.configure("TButton", padding=5)

    def build_main_layout(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, padding=20)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", self.resize_canvas_window)
        self.root.bind_all("<MouseWheel>", self.on_mousewheel)

    def resize_canvas_window(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def setup_ui(self):
        title_label = ttk.Label(
            self.scrollable_frame,
            text="Priority vs SRTF Comparison Project",
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 8))

        rules_text = (
            "Priority rule: smaller priority number means higher priority. "
            "Tie-breaking: earlier arrival first, then input order.\n"
            "SRTF rule: process with the shortest remaining time runs first. "
            "If a shorter job arrives, it preempts immediately."
        )
        ttk.Label(
            self.scrollable_frame,
            text=rules_text,
            style="Info.TLabel",
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(0, 10))

        self.create_scenario_section()
        self.create_input_section()
        self.create_process_table_section()

        ttk.Button(
            self.scrollable_frame,
            text="Run Comparison Simulation",
            command=self.run_simulation
        ).pack(pady=12)

        self.results_frame = ttk.Frame(self.scrollable_frame)
        self.results_frame.pack(fill=tk.BOTH, expand=True)

    def create_scenario_section(self):
        scenario_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text=" Predefined Scenarios ",
            padding=10,
            style="Section.TLabelframe"
        )
        scenario_frame.pack(fill=tk.X, pady=5)

        buttons = [
            ("Scenario A: Basic Workload", self.load_scenario_a),
            ("Scenario B: Priority/Burst Conflict", self.load_scenario_b),
            ("Scenario C: Starvation Case", self.load_scenario_c),
            ("Scenario D: Validation Case", self.load_scenario_d),
        ]

        for col, (text, command) in enumerate(buttons):
            scenario_frame.columnconfigure(col, weight=1)
            ttk.Button(scenario_frame, text=text, command=command).grid(
                row=0, column=col, padx=5, pady=2, sticky="ew"
            )

    def create_input_section(self):
        input_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text=" Input Panel ",
            padding=15,
            style="Section.TLabelframe"
        )
        input_frame.pack(fill=tk.X, pady=5)

        labels = [
            ("PID:", "pid"),
            ("Arrival:", "arrival"),
            ("Burst:", "burst"),
            ("Priority (1-10):", "priority")
        ]

        self.entries = {}
        for i, (label_text, key) in enumerate(labels):
            ttk.Label(input_frame, text=label_text).grid(row=0, column=i * 2, padx=(5, 2), sticky=tk.W)
            entry = ttk.Entry(input_frame, width=14)
            entry.grid(row=0, column=i * 2 + 1, padx=(2, 10), sticky="ew")
            self.entries[key] = entry

        ttk.Button(input_frame, text="Add Process", command=self.add_process).grid(
            row=0, column=8, padx=5
        )
        ttk.Button(input_frame, text="Clear Data", command=self.clear_data).grid(
            row=0, column=9, padx=5
        )

    def create_process_table_section(self):
        table_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text=" Process Table ",
            padding=10,
            style="Section.TLabelframe"
        )
        table_frame.pack(fill=tk.X, pady=10)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("PID", "Arrival", "Burst", "Priority"),
            show="headings",
            height=6
        )

        widths = {"PID": 180, "Arrival": 120, "Burst": 120, "Priority": 120}
        for col in ("PID", "Arrival", "Burst", "Priority"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=widths[col])

        self.tree.pack(fill=tk.X)

    def validate_process_values(self, pid, arrival, burst, priority):
        if pid == "":
            raise ValueError("Process ID cannot be empty.")
        if arrival < 0:
            raise ValueError("Arrival time cannot be negative.")
        if burst <= 0:
            raise ValueError("Burst time must be greater than zero.")
        if not (1 <= priority <= 10):
            raise ValueError("Priority must be between 1 and 10. 1 means highest priority.")
        if any(p.pid == pid for p in self.processes_list):
            raise ValueError("Duplicate PID. Please use a unique process ID.")

    def add_process_manual(self, pid, arrival, burst, priority):
        self.validate_process_values(pid, arrival, burst, priority)
        self.processes_list.append(Process(pid, arrival, burst, priority))
        self.tree.insert("", tk.END, values=(pid, arrival, burst, priority))

    def add_process(self):
        try:
            pid = self.entries["pid"].get().strip()
            arrival = int(self.entries["arrival"].get().strip())
            burst = int(self.entries["burst"].get().strip())
            priority = int(self.entries["priority"].get().strip())

            self.add_process_manual(pid, arrival, burst, priority)

            for entry in self.entries.values():
                entry.delete(0, tk.END)

        except ValueError as error:
            messagebox.showerror("Invalid Input", str(error))

    def load_processes(self, data):
        self.clear_data()
        try:
            for process_data in data:
                self.add_process_manual(*process_data)
        except ValueError as error:
            messagebox.showerror("Scenario Error", str(error))

    def load_scenario_a(self):
        data = [
            ("P1", 0, 5, 3),
            ("P2", 1, 3, 1),
            ("P3", 2, 8, 4),
            ("P4", 3, 2, 2),
        ]
        self.load_processes(data)

    def load_scenario_b(self):
        data = [
            ("P_Long_HighPri", 0, 10, 1),
            ("P_Short_LowPri", 1, 2, 10),
            ("P_Medium", 2, 4, 5),
        ]
        self.load_processes(data)

    def load_scenario_c(self):
        data = [
            ("P1_HighPri_Long", 0, 15, 1),
            ("P2_LowPri_Short", 1, 2, 5),
            ("P3_LowPri_Short", 2, 2, 5),
            ("P4_LowPri_Short", 3, 2, 5),
            ("P5_LowPri_Short", 4, 2, 5),
        ]
        self.load_processes(data)

    def load_scenario_d(self):
        self.clear_data()
        self.entries["pid"].insert(0, "P_Error")
        self.entries["arrival"].insert(0, "0")
        self.entries["burst"].insert(0, "-5")
        self.entries["priority"].insert(0, "99")
        messagebox.showinfo(
            "Validation Demo",
            "Invalid values were inserted. Click 'Add Process' to see safe validation handling."
        )

    def create_gantt(self, parent, gantt_data, title):
        frame = ttk.LabelFrame(
            parent,
            text=f" Gantt Chart: {title} ",
            padding=10,
            style="Section.TLabelframe"
        )
        frame.pack(fill=tk.X, pady=6)

        canvas = tk.Canvas(frame, height=95, bg="#ffffff", highlightthickness=1, highlightbackground="#dcdcdc")
        canvas.pack(fill=tk.X)

        if not gantt_data:
            canvas.create_text(20, 40, anchor=tk.W, text="No execution data.", font=("Arial", 10))
            return

        total_time = gantt_data[-1][2]
        available_width = 1050
        scale = max(18, min(45, available_width / max(total_time, 1)))

        x = 35
        y1 = 20
        y2 = 55

        for pid, start, end in gantt_data:
            width = max((end - start) * scale, 24)

            canvas.create_rectangle(x, y1, x + width, y2, fill="#3498db", outline="#ecf0f1")
            canvas.create_text(
                x + width / 2,
                (y1 + y2) / 2,
                text=pid,
                fill="white",
                font=("Arial", 9, "bold")
            )
            canvas.create_text(x, 73, text=str(start), font=("Arial", 8))
            x += width

        canvas.create_text(x, 73, text=str(gantt_data[-1][2]), font=("Arial", 8))

    def create_results_table(self, parent, results, title, averages):
        frame = ttk.LabelFrame(
            parent,
            text=f" {title} ",
            padding=6,
            style="Section.TLabelframe"
        )
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        table = ttk.Treeview(
            frame,
            columns=("PID", "WT", "TAT", "RT"),
            show="headings",
            height=max(5, min(len(results) + 1, 9))
        )

        for col in ("PID", "WT", "TAT", "RT"):
            table.heading(col, text=col)
            table.column(col, width=80, anchor=tk.CENTER)

        for process in results:
            table.insert(
                "",
                tk.END,
                values=(
                    process.pid,
                    process.waiting_time,
                    process.turnaround_time,
                    process.response_time
                )
            )

        table.insert(
            "",
            tk.END,
            values=("AVG", f"{averages[0]:.2f}", f"{averages[1]:.2f}", f"{averages[2]:.2f}")
        )

        table.pack(fill=tk.BOTH, expand=True)

    @staticmethod
    def metric_sentence(priority_value, srtf_value, metric_name):
        if priority_value < srtf_value:
            return f"- Priority produced the lower average {metric_name}."
        if srtf_value < priority_value:
            return f"- SRTF produced the lower average {metric_name}."
        return f"- Both algorithms produced the same average {metric_name}."

    @staticmethod
    def average_attribute(processes, pids, attr_name):
        values = [getattr(p, attr_name) for p in processes if p.pid in pids]
        return sum(values) / len(values) if values else 0

    @staticmethod
    def waiting_spread(processes):
        values = [p.waiting_time for p in processes]
        return max(values) - min(values) if values else 0

    @staticmethod
    def better_metric_name(priority_value, srtf_value, metric_name):
        if priority_value < srtf_value:
            return f"Priority had better {metric_name}"
        if srtf_value < priority_value:
            return f"SRTF had better {metric_name}"
        return f"Both tied on {metric_name}"

    def build_comparison_text(self, priority_results, srtf_results, priority_avg, srtf_avg):
        min_priority = min(p.priority for p in self.processes_list)
        urgent_pids = [p.pid for p in self.processes_list if p.priority == min_priority]

        min_burst = min(p.burst for p in self.processes_list)
        short_pids = [p.pid for p in self.processes_list if p.burst == min_burst]

        priority_urgent_rt = self.average_attribute(priority_results, urgent_pids, "response_time")
        srtf_urgent_rt = self.average_attribute(srtf_results, urgent_pids, "response_time")

        priority_short_tat = self.average_attribute(priority_results, short_pids, "turnaround_time")
        srtf_short_tat = self.average_attribute(srtf_results, short_pids, "turnaround_time")

        priority_spread = self.waiting_spread(priority_results)
        srtf_spread = self.waiting_spread(srtf_results)

        if priority_spread == srtf_spread:
            fairer_text = "Both algorithms had the same waiting-time spread, so fairness was similar."
        elif priority_spread < srtf_spread:
            fairer_text = "Priority appeared fairer by waiting-time spread in this workload."
        else:
            fairer_text = "SRTF appeared fairer by waiting-time spread in this workload."

        lines = [
            f"Priority Average -> WT={priority_avg[0]:.2f}, TAT={priority_avg[1]:.2f}, RT={priority_avg[2]:.2f}",
            f"SRTF Average     -> WT={srtf_avg[0]:.2f}, TAT={srtf_avg[1]:.2f}, RT={srtf_avg[2]:.2f}",
            "",
            "Analysis:",
            self.metric_sentence(priority_avg[0], srtf_avg[0], "waiting time"),
            self.metric_sentence(priority_avg[2], srtf_avg[2], "response time"),
            f"- Waiting-time spread: Priority={priority_spread}, SRTF={srtf_spread}. {fairer_text}",
        ]

        if priority_urgent_rt < srtf_urgent_rt:
            lines.append("- Yes, priority values improved treatment of urgent processes in this workload.")
        elif priority_urgent_rt > srtf_urgent_rt:
            lines.append("- No, SRTF treated the urgent processes faster in this workload because of remaining time.")
        else:
            lines.append("- Priority and SRTF treated the urgent processes equally in response time here.")

        if srtf_short_tat < priority_short_tat:
            lines.append("- Yes, SRTF favored short jobs more aggressively and completed them earlier.")
        elif srtf_short_tat > priority_short_tat:
            lines.append("- In this workload, Priority completed the shortest jobs earlier than SRTF.")
        else:
            lines.append("- The shortest jobs had the same average turnaround time in both algorithms here.")

        if priority_avg[0] < srtf_avg[0]:
            recommendation = "Priority is recommended for this workload because it has lower average waiting time."
        elif srtf_avg[0] < priority_avg[0]:
            recommendation = "SRTF is recommended for this workload because it has lower average waiting time."
        elif priority_avg[2] < srtf_avg[2]:
            recommendation = "Priority is recommended because waiting time is tied but response time is better."
        elif srtf_avg[2] < priority_avg[2]:
            recommendation = "SRTF is recommended because waiting time is tied but response time is better."
        else:
            recommendation = "Both algorithms are equivalent for this workload based on the calculated averages."

        lines.append(f"- Recommendation: {recommendation}")

        return "\n".join(lines)

    def build_final_conclusion_text(self, priority_results, srtf_results, priority_avg, srtf_avg):
        priority_spread = self.waiting_spread(priority_results)
        srtf_spread = self.waiting_spread(srtf_results)
        better_metrics = [
            self.better_metric_name(priority_avg[0], srtf_avg[0], "average WT"),
            self.better_metric_name(priority_avg[1], srtf_avg[1], "average TAT"),
            self.better_metric_name(priority_avg[2], srtf_avg[2], "average RT"),
        ]

        if priority_avg[0] < srtf_avg[0]:
            best_overall = "Priority performed better on average waiting time for this dataset."
        elif srtf_avg[0] < priority_avg[0]:
            best_overall = "SRTF performed better on average waiting time for this dataset."
        else:
            best_overall = "Both algorithms tied on average waiting time for this dataset."

        if priority_spread < srtf_spread:
            fairer = "Priority appeared fairer in practice because its waiting times were closer together."
        elif srtf_spread < priority_spread:
            fairer = "SRTF appeared fairer in practice because its waiting times were closer together."
        else:
            fairer = "Both algorithms appeared equally fair by waiting-time spread."

        return "\n".join([
            best_overall,
            "Metrics: " + "; ".join(better_metrics) + ".",
            "Main trade-off: Priority follows urgency policy and can delay low-priority short jobs; "
            "SRTF improves efficiency for short remaining jobs but can delay longer jobs.",
            fairer,
        ])

    def run_simulation(self):
        if not self.processes_list:
            messagebox.showwarning("Warning", "No processes to simulate.")
            return

        for widget in self.results_frame.winfo_children():
            widget.destroy()

        priority_results, priority_gantt = priority_scheduler(self.processes_list)
        srtf_results, srtf_gantt = srtf_scheduler(self.processes_list)

        priority_avg = calculate_metrics(priority_results)
        srtf_avg = calculate_metrics(srtf_results)

        self.create_gantt(self.results_frame, priority_gantt, "Priority Scheduling")
        self.create_gantt(self.results_frame, srtf_gantt, "SRTF Scheduling")

        results_row = ttk.Frame(self.results_frame)
        results_row.pack(fill=tk.X, pady=10)

        self.create_results_table(results_row, priority_results, "Priority Results", priority_avg)
        self.create_results_table(results_row, srtf_results, "SRTF Results", srtf_avg)

        comparison_frame = ttk.LabelFrame(
            self.results_frame,
            text=" Comparison Summary Section ",
            padding=12,
            style="Section.TLabelframe"
        )
        comparison_frame.pack(fill=tk.X, pady=6)

        comparison_text = self.build_comparison_text(
            priority_results,
            srtf_results,
            priority_avg,
            srtf_avg
        )
        ttk.Label(comparison_frame, text=comparison_text, font=("Consolas", 10), justify=tk.LEFT).pack(anchor=tk.W)

        conclusion_frame = ttk.LabelFrame(
            self.results_frame,
            text=" Final Conclusion Area ",
            padding=12,
            style="Section.TLabelframe"
        )
        conclusion_frame.pack(fill=tk.X, pady=6)

        conclusion_text = self.build_final_conclusion_text(
            priority_results,
            srtf_results,
            priority_avg,
            srtf_avg
        )
        ttk.Label(conclusion_frame, text=conclusion_text, font=("Consolas", 10), justify=tk.LEFT).pack(anchor=tk.W)

    def clear_data(self):
        self.processes_list = []

        for item in self.tree.get_children():
            self.tree.delete(item)

        if hasattr(self, "results_frame"):
            for widget in self.results_frame.winfo_children():
                widget.destroy()

        if hasattr(self, "entries"):
            for entry in self.entries.values():
                entry.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerGUI(root)
    root.mainloop()
