import dataclasses
from prompts import *


@dataclasses.dataclass
class ModelConfig:
    id: str
    type: str
    prompt_format: str
    is_llama: bool = False


GPT_PROMPT_FORMAT = """{prompt}"""
LLAMA_PROMPT_FORMAT = (
    """{prompt}"""
)

MODEL_MAPPING = {
    "gpt4": ModelConfig(
        id="gpt-4-0125-preview",
        type="chat",
        prompt_format=GPT_PROMPT_FORMAT,
        is_llama=False,
    ),
    "gpt3": ModelConfig(
        id="gpt-3.5-turbo-1106",
        type="chat",
        prompt_format=GPT_PROMPT_FORMAT,
        is_llama=False,
    ),
    "gpt3-instruct": ModelConfig(
        id="gpt-3.5-turbo-instruct",
        type="instruct",
        prompt_format=GPT_PROMPT_FORMAT,
        is_llama=False,
    ),
    "llama2_70b_chat": ModelConfig(
        id="meta-llama/Llama-2-70b-chat-hf",
        type="chat",
        prompt_format=LLAMA_PROMPT_FORMAT,
        is_llama=True,
    ),
    "llama2_70b": ModelConfig(
        id="meta-llama/Llama-2-70b-hf",
        type="instruct",
        prompt_format=LLAMA_PROMPT_FORMAT,
        is_llama=True,
    ),
    "llama3_70b_chat": ModelConfig(
        id="meta-llama/Meta-Llama-3-70B",
        type="chat",
        prompt_format=LLAMA_PROMPT_FORMAT,
        is_llama=True,
    ),
    "llama3_70b": ModelConfig(
        id="meta-llama/Meta-Llama-3-70B-Instruct",
        type="instruct",
        prompt_format=LLAMA_PROMPT_FORMAT,
        is_llama=True,
    ),
}


@dataclasses.dataclass
class TwoStepConfig:
    verify_prompt: str
    generate_prompt: str


@dataclasses.dataclass
class TaskConfig:
    id: str
    max_tokens: int
    baseline_prompt: str
    joint_prompt: str
    ground_truth_attribute: str
    two_step: TwoStepConfig


TASK_MAPPING = {
    "error_reason": TaskConfig(
        id="error-reason",
        max_tokens=250,
        baseline_prompt=DIRECT_GENERATION,
        joint_prompt="",
        two_step=TwoStepConfig(
            verify_prompt=VERIFY_REMATH_BASELINE,
            generate_prompt=GENERATE_AFTER_VERIFICATION,
        ),
        ground_truth_attribute="ground_truth_error_reason",
    ),
    "error_description": TaskConfig(
        id="error_description",
        max_tokens=250,
        baseline_prompt=DIRECT_GENERATION,
        joint_prompt="",
        two_step=TwoStepConfig(
            verify_prompt=VERIFY_STEP_ERROR_DESCRIPTION,
            generate_prompt=GENERATE_AFTER_VERIFICATION,
        ),
        ground_truth_attribute="ground_truth_error_description",
    ),
    "step_alignment": TaskConfig(
        id="step_alignment",
        max_tokens=250,
        baseline_prompt=DIRECT_GENERATION,
        joint_prompt="",
        two_step=TwoStepConfig(
            verify_prompt="",
            generate_prompt=GENERATE_AFTER_VERIFICATION,
        ),
        ground_truth_attribute="ground_truth_step_alignment",
    )
}

ERROR_REASON_DESCRIPTION = {
    "0": "Student does not seem to understand or guessed the answer.",
    "1": "Student misinterpreted the question.",
    "2": "Student made a careless mistake.",
    "3": "Student has the right idea, but is not quite there.",
    "4": "Student’s answer is not precise enough or the tutor is being too picky about the form of the student’s answer.",
    "5": "None of the above, but I have a different description (please specify in your reasoning).",
    "6": "Not sure, but I’m going to try to diagnose the student."
}
