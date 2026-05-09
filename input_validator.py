class InputValidator:
    @staticmethod
    def get_int(prompt):
        while True:
            try:
                value = int(input(prompt))
                return value
            except ValueError:
                print("Please enter a valid number.")

    @staticmethod
    def get_positive_int(prompt):
        while True:
            value = InputValidator.get_int(prompt)
            if value >= 0:
                return value
            print("Value cannot be negative.")

    @staticmethod
    def get_process_count(prompt):
        while True:
            value = InputValidator.get_int(prompt)
            if value > 0:
                return value
            print("Number of processes must be greater than zero.")

    @staticmethod
    def get_burst(prompt):
        while True:
            value = InputValidator.get_int(prompt)
            if value > 0:
                return value
            print("Burst time must be greater than zero.")

    @staticmethod
    def get_priority(prompt):
        while True:
            value = InputValidator.get_int(prompt)
            if 1 <= value <= 10:
                return value
            print("Priority must be between 1 and 10 (1 = highest).")

    @staticmethod
    def get_pid(prompt, existing_ids):
        while True:
            pid = input(prompt).strip()
            if pid == "":
                print("Process ID cannot be empty.")
            elif pid in existing_ids:
                print(f"Duplicate ID: {pid}. Please use a unique ID.")
            else:
                return pid
