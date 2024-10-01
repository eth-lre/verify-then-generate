import json

class MathDial(object):
    def __init__(self, path):
        self.data = self.load(path)
        self.name = "mathdial"

    def load(self, path):
        with open(path, "r", encoding="utf-8") as f:
            raw_dataset = json.load(f)
        print(len(raw_dataset))
        processed = []
        for sample in raw_dataset:
            conv_list = sample["dialog_history"]

            # Get the 2nd teacher turn, sometimes multiple message was send by the same user
            cutoff = 2
            for i, turn in enumerate(conv_list):
                if turn["user"] == "Student":
                    cutoff = i + 1
                    break

            processed.append({
                "problem": sample["problem"],
                "topic": sample["topic"],
                "ground_truth_responses": [conv_list[cutoff]],
                "dialog_history": conv_list[:cutoff],
                "student_incorrect_solution": sample["student_incorrect_solution"],
                "reference_solution": sample["reference_solution"],
                # Use only if ground truth annotations are available
                "ground_truth_error_reason": "",
                "ground_truth_error_description": "",
                "ground_truth_step_alignment": ""
            })
        return processed
