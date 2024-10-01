import argparse
import os
import openai
import time
import json
from apiwrapper import PrompterAPI
from prompts import PROMPTS

openai.api_key = os.getenv("OPENAI_API_KEY")


def classification_based_verification(prompter, input_path, prompt_config, unique_id_model_prompt, output_path,
                                      top_n_only=5000):
    test_file = open(input_path, 'r')
    test_data = json.load(test_file)

    for idx, test_case in enumerate(test_data[:top_n_only]):
        print(idx, len(test_data))
        question = test_case['problem']

        if "overall" in prompt_config["name"]:
            # Setting: binary classification + student response from the conversation

            # Part 1 - incorrect student response
            correct_answer = test_case["reference_solution"]
            conversation_list = test_case["dialog_history"]
            cutoff = 2
            # Find the cutoff point where the student response starts
            for i, turn in enumerate(conversation_list):
                if "Teacher:" not in turn:
                    cutoff = i
                    break
            student_response = conversation_list[cutoff]["text"]
            prompt = prompt_config["prompt"].replace("{QUESTION}", question).replace("{CORRECT_ANSWER}",
                                                                                     correct_answer).replace(
                "{STUDENT_ANSWER}", student_response)
            response = prompter.generate(prompt, stop=["Q:"], max_tokens=10)
            test_case[unique_id_model_prompt] = response

            # Part 2 - correct student response - marked as ground truth
            student_response = test_case["student_correct_response"]
            prompt = prompt_config["prompt"].replace("{QUESTION}", question).replace("{CORRECT_ANSWER}",
                                                                                     correct_answer).replace(
                "{STUDENT_ANSWER}", student_response)
            response = prompter.generate(prompt, stop=["Q:"], max_tokens=10)
            test_case[unique_id_model_prompt + "ground_truth"] = response
        elif "stepwise" in prompt_config["name"]:
            # Setting - multiclass classification + step-by-step student solution

            # Part 1 - incorrect student solution
            correct_answer = "\\n".join(["Step " + str(sub_index + 1) + " - " + substep for sub_index, substep in
                                         enumerate(test_case["reference_solution"].split("\n")[:-1])])
            student_answer = "\\n".join(["Step " + str(sub_index + 1) + " - " + substep for sub_index, substep in
                                         enumerate(test_case["student_incorrect_solution"][:-1])])
            prompt = prompt_config["prompt"].replace("{QUESTION}", question).replace("{CORRECT_ANSWER}",
                                                                                     correct_answer).replace(
                "{STUDENT_ANSWER}", student_answer)
            response = prompter.generate(prompt, stop=["Q:"], max_tokens=20)
            test_case[unique_id_model_prompt] = response

            # Part 2 Correct student solution - marked as ground_truth
            student_correct_answer = "\\n".join(
                ["Step " + str(sub_index + 1) + " - " + substep for sub_index, substep in
                 enumerate(test_case["student_correct_response"].split("\n"))])
            prompt = prompt_config["prompt"].replace("{QUESTION}", question).replace("{CORRECT_ANSWER}",
                                                                                     correct_answer).replace(
                "{STUDENT_ANSWER}", student_correct_answer)
            response = prompter.generate(prompt, stop=["Q:"], max_tokens=20)
            test_case[unique_id_model_prompt + "ground_truth"] = response
        else:
            raise ValueError("Prompt not found")

    with open(os.path.join(output_path, unique_identifier_model_prompt) + ".json", 'w') as f:
        json.dump(test_data[:top_n_only], f, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--setting", type=str, default="stepwise_verification",
                        help="Prompt from yaml files which will be loaded and used.",
                        choices=["overall_verification",
                                 "overall_verification_with_solution",
                                 "stepwise_verification",
                                 'stepwise_verification_with_solution',
                                 ])
    parser.add_argument("--model", type=str, default="gpt3",
                        help="Model to use",
                        choices=['gpt3', 'gpt3-instruct', "llama2_70b_chat", "llama2_70b", "llama3_70b"])
    parser.add_argument("--top_n_only", type=int, default=10,
                        help="First n examples in the dataset to run on.")
    parser.add_argument("--output_path", type=str, default=".",
                        help="Output path for the generations.")
    args = parser.parse_args()

    input_path = f"../dataset/dataset.json"
    time_start = time.time()

    prompter = PrompterAPI(args.model, debug=True)
    prompt_config = PROMPTS[args.setting]
    print(prompt_config)
    unique_identifier_model_prompt = f"{args.model}_{args.setting}"
    classification_based_verification(prompter, input_path, prompt_config,
                                      unique_identifier_model_prompt, args.output_path, args.top_n_only)

    time_end = time.time()
    print('\ntime:', time_end - time_start)
