import unittest

from metrics import calculate_metrics
from priority_scheduler import priority_scheduler
from process import Process
from srtf_scheduler import srtf_scheduler


class SchedulerLogicTests(unittest.TestCase):
    def assert_results(self, actual_processes, expected):
        actual = {
            process.pid: (
                process.waiting_time,
                process.turnaround_time,
                process.response_time,
                process.completion_time,
            )
            for process in actual_processes
        }
        self.assertEqual(actual, expected)

    def test_scenario_a_basic_mixed_workload(self):
        processes = [
            Process("P1", 0, 5, 3),
            Process("P2", 1, 3, 1),
            Process("P3", 2, 8, 4),
            Process("P4", 3, 2, 2),
        ]

        expected_gantt = [
            ["P1", 0, 1],
            ["P2", 1, 4],
            ["P4", 4, 6],
            ["P1", 6, 10],
            ["P3", 10, 18],
        ]
        expected_results = {
            "P1": (5, 10, 0, 10),
            "P2": (0, 3, 0, 4),
            "P3": (8, 16, 8, 18),
            "P4": (1, 3, 1, 6),
        }

        priority_results, priority_gantt = priority_scheduler(processes)
        srtf_results, srtf_gantt = srtf_scheduler(processes)

        self.assertEqual(priority_gantt, expected_gantt)
        self.assertEqual(srtf_gantt, expected_gantt)
        self.assert_results(priority_results, expected_results)
        self.assert_results(srtf_results, expected_results)
        self.assertEqual(calculate_metrics(priority_results), (3.5, 8.0, 2.25))
        self.assertEqual(calculate_metrics(srtf_results), (3.5, 8.0, 2.25))

    def test_scenario_b_priority_burst_conflict(self):
        processes = [
            Process("P_Long_HighPri", 0, 10, 1),
            Process("P_Short_LowPri", 1, 2, 10),
            Process("P_Medium", 2, 4, 5),
        ]

        priority_results, priority_gantt = priority_scheduler(processes)
        srtf_results, srtf_gantt = srtf_scheduler(processes)

        self.assertEqual(priority_gantt, [
            ["P_Long_HighPri", 0, 10],
            ["P_Medium", 10, 14],
            ["P_Short_LowPri", 14, 16],
        ])
        self.assertEqual(srtf_gantt, [
            ["P_Long_HighPri", 0, 1],
            ["P_Short_LowPri", 1, 3],
            ["P_Medium", 3, 7],
            ["P_Long_HighPri", 7, 16],
        ])
        self.assert_results(priority_results, {
            "P_Long_HighPri": (0, 10, 0, 10),
            "P_Short_LowPri": (13, 15, 13, 16),
            "P_Medium": (8, 12, 8, 14),
        })
        self.assert_results(srtf_results, {
            "P_Long_HighPri": (6, 16, 0, 16),
            "P_Short_LowPri": (0, 2, 0, 3),
            "P_Medium": (1, 5, 1, 7),
        })

    def test_same_arrival_tie_breaks_by_input_order(self):
        processes = [
            Process("P1", 0, 3, 1),
            Process("P2", 0, 3, 1),
            Process("P3", 0, 3, 1),
        ]

        priority_results, priority_gantt = priority_scheduler(processes)
        srtf_results, srtf_gantt = srtf_scheduler(processes)

        expected_gantt = [["P1", 0, 3], ["P2", 3, 6], ["P3", 6, 9]]
        self.assertEqual(priority_gantt, expected_gantt)
        self.assertEqual(srtf_gantt, expected_gantt)
        self.assertEqual([p.pid for p in priority_results], ["P1", "P2", "P3"])
        self.assertEqual([p.pid for p in srtf_results], ["P1", "P2", "P3"])


if __name__ == "__main__":
    unittest.main()
