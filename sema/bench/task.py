class Task:
    def __init__(
        self,
        input_data_location,
        output_data_location,
        sembench_data_location,
        task_id,
        func,
        args,
    ):
        self.input_data_location = input_data_location
        self.output_data_location = output_data_location
        self.sembench_data_location = sembench_data_location
        self.task_id = task_id
        self.func = func.lower()
        self.args = args
