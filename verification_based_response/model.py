from typing import Dict, List

from aligner import StepAlignment
from apiwrapper import PrompterAPI
from config import TaskConfig, TASK_MAPPING, ERROR_REASON_DESCRIPTION
from parsing_utils import parse_json_result
from prompts import COT_SOLUTION


class Pipeline(object):
    def __init__(self, prompter: PrompterAPI, dataset: str, task: str):
        self.prompter = prompter
        self.dataset = dataset
        self.task_config: TaskConfig = TASK_MAPPING.get(dataset + "-" + task, TASK_MAPPING[task])
        if self.task_config is None:
            print(f"Invalid task. Valid tasks are: {', '.join(TASK_MAPPING.keys())}")

    def get_baseline_response(self, example: Dict):
        prompt = self.task_config.baseline_prompt.replace("${problem}", example["problem"]).replace(
            "${lesson_topic}", example["topic"])
        messages = example["dialog_history"]
        generated = self.prompter.generate(messages, prompt, stop=["Student:", "Problem:", "\n\n"])
        return {"response": generated}


class ErrorReasonPipeline(Pipeline):
    """Baseline"""

    def get_joint_response(self, example: Dict):
        raise NotImplementedError

    def get_two_step_response(self, example: Dict, use_oracle: bool):
        messages = example["dialog_history"]
        if use_oracle:
            error_reason = example[self.task_config.ground_truth_attribute]
        else:
            verify_prompt = self.task_config.two_step.verify_prompt.replace("${lesson_topic}",
                                                                            example["topic"]).replace("${problem}",
                                                                                                      example[
                                                                                                          "problem"])
            error_reason_raw = self.prompter.generate(messages, verify_prompt,
                                                      stop=["Student:", "Question:"])
            # should contain answer and reason keys
            error_reason_json = parse_json_result(error_reason_raw)
            error_reason_option = None
            if error_reason_json:
                error_reason_option = error_reason_json.get("answer", None)
            if error_reason_option is not None and len(str(error_reason_option)) > 0:
                # Get the first letter of the option - should be numerical from 0 to 6
                error_reason = ERROR_REASON_DESCRIPTION.get(str(error_reason_option)[0], error_reason_option)
            else:
                error_reason = error_reason_raw

        generate_prompt = self.task_config.two_step.generate_prompt.replace("${lesson_topic}",
                                                                            example["topic"]).replace(
            "${assessment}", error_reason).replace("${problem}", example["problem"])
        generated = self.prompter.generate(messages, generate_prompt, stop=["Student:", "\n\n", "Problem:"])
        return {"response": generated, "predicted_error_reason": error_reason}


class ErrorDescriptionPipeline(Pipeline):

    def get_joint_response(self, example: Dict):
        raise NotImplementedError

    def get_two_step_response(self, example: Dict, use_oracle: bool = False):
        messages = example["dialog_history"]
        if use_oracle:
            error_description = example[self.task_config.ground_truth_attribute]
        else:
            # First CoT solution
            verify_prompt = COT_SOLUTION.replace("${problem}", example["problem"])
            solution = self.prompter.generate([], verify_prompt,
                                              stop=["Student:", "Question:"])
            solution = solution.replace("\n", "\\n")

            # Secondly comparison with the error description
            verify_prompt = self.task_config.two_step.verify_prompt.replace("${problem}", example["problem"]).replace(
                "${solution}", solution)
            error_description = self.prompter.generate(messages, verify_prompt,
                                                       stop=["Student:", "Question:"],
                                                       max_tokens=256)
            error_description = error_description.replace("\n", "\\n")

        # Generate the response
        generate_prompt = self.task_config.two_step.generate_prompt.replace("${problem}", example["problem"]).replace(
            "${assessment}", error_description).replace("${lesson_topic}",
                                                        example["topic"])
        generated = self.prompter.generate(messages, generate_prompt, stop=["Student:"])
        return {"response": generated, "predicted_error_desription": error_description}


class StepAlignmentPipeline(Pipeline):
    def get_joint_response(self, example: Dict):
        raise NotImplementedError

    def get_two_step_response(self, example: Dict, use_oracle: bool):
        messages = example["dialog_history"]
        aligner = StepAlignment(model='roscoe', similarity_threshold=0.9, gap_utility=0.1)
        if use_oracle:
            corrected_reasoning = example[self.task_config.ground_truth_attribute]
        else:
            # First generate the CoT solution
            cot_solution_prompt = COT_SOLUTION.replace("${problem}", example["problem"])
            cot_solution = self.prompter.generate([], cot_solution_prompt,
                                                  stop=["Student:", "Question:"])
            cot_solution_list = cot_solution.replace("\n\n", "\n").split("\n")

            # Secondly align student solution with CoT solution
            student_solution = messages[-1]["text"]
            student_solution_list = student_solution.replace("\n", "").strip().split(". ")
            aligned_sol_steps, aligned_student_steps, _ = aligner.align(cot_solution_list, student_solution_list)
            corrected_reasoning = self._format_aligned_paths(aligned_sol_steps, aligned_student_steps)

        generate_prompt = self.task_config.two_step.generate_prompt.replace("${problem}", example["problem"]).replace(
            "${assessment}", corrected_reasoning).replace("${lesson_topic}", example["topic"])
        generated = self.prompter.generate(messages, generate_prompt, stop=["Student:", "Problem:"])
        return {"response": generated, "predicted_alignment": corrected_reasoning}

    @staticmethod
    def _format_aligned_paths(aligned_sol_path: List[str], aligned_stud_path: List[str]):
        formatted_aligned_information = []
        step_number = 1
        for sol, stud in zip(aligned_sol_path, aligned_stud_path):
            if sol == stud:
                continue
            if "_" in sol:
                formatted_aligned_information.append(f"Unnecessary step of student: {stud}")
            elif "_" in stud:
                formatted_aligned_information.append(f"Missing student step: {sol}")
            else:
                formatted_aligned_information.append(
                    f"Matching step. Student: {stud}[Student Step End] Expected: {sol}[Expected step end]")
                step_number += 1
        return "\n".join(formatted_aligned_information)
