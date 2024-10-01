import argparse
import re

import json
from sklearn.metrics import classification_report


def extract_predicted_step_number(response):
    response = response.strip().split("\n")[0]
    found_number = re.findall(r'\d+', response)
    predicted_step = 0
    if re.findall(r'^NO', response, re.IGNORECASE) or "0" in response:
        is_predicted_correct = True
    else:
        is_predicted_correct = False
        if len(found_number) > 0:
            predicted_step = int(found_number[0])
        else:
            print(f"ISSUE: no step number found in the response: {response}")
    if predicted_step == 0:
        is_predicted_correct = True
    return predicted_step, is_predicted_correct


def extract_step_corectness(response):
    response = response.strip().split("\n")[0]
    if re.findall(r'^NO', response, re.IGNORECASE):
        # "No" means the step is correct and contributes to solving of the Problem.
        is_predicted_correct = True
    elif re.findall(r'^YES', response, re.IGNORECASE):
        is_predicted_correct = False
    else:
        print("ISSUE: no YES/NO found in the response")
        return True
    return is_predicted_correct


def evaluate_gsm8k(test_path, unique_model_id):
    print(f"Loading {test_path}")
    test_file = open(test_path, 'r')
    test_data = json.load(test_file)
    print(test_data[0])

    human_labeled_steps = []
    predicted_error_steps = []

    for idx, test_case in enumerate(test_data):
        # Part 1 Evaluate incorrect student solution
        # human annotators steps are index from 0
        human_step_number = test_case["incorrect_index"]
        human_step_number += 1

        if "overall" in unique_model_id:
            prediction = test_case[unique_model_id]
            is_predicted_correct = extract_step_corectness(prediction)
            if is_predicted_correct:
                predicted_step = 0
            else:
                # For binary classification we don't know the exact step number, set just to 1
                predicted_step = 1
        elif "stepwise" in unique_model_id:
            model_response = test_case[unique_model_id]
            predicted_step, is_predicted_correct = extract_predicted_step_number(model_response)
        else:
            raise ValueError("Unknown evaluation setting")

        # Add to data for evaluation
        human_labeled_steps.append(human_step_number)
        predicted_error_steps.append(predicted_step)

        # Part 2 Evaluate correct student solution
        human_step_number = 0  # hard coded as correct
        if "binary" in unique_model_id:
            predicted_step = 0
            for step in test_case["correct_steps"]:
                prediction = step[unique_model_id]
                is_predicted_correct = extract_step_corectness(prediction)
                if not is_predicted_correct:
                    predicted_step = step["step_number"]
                    break
        elif "response" in unique_model_id or "overall" in unique_model_id:
            is_predicted_correct = extract_step_corectness(test_case[unique_model_id + "ground_truth"])
            if is_predicted_correct:
                predicted_step = 0
            else:
                predicted_step = 1
        else:
            predicted_step, is_predicted_correct = extract_predicted_step_number(
                test_case[unique_model_id + "ground_truth"])

        # Add to data for evaluation
        human_labeled_steps.append(human_step_number)
        predicted_error_steps.append(predicted_step)

    assert len(human_labeled_steps) == len(predicted_error_steps)
    print("\nExact steps (first row human annotation, second row predicted)")
    print(human_labeled_steps)
    print(predicted_error_steps)

    print("Multi-class classification (number greater than 0 refers to the exact step with error)")
    print(classification_report(human_labeled_steps, predicted_error_steps, digits=4, labels=range(0, 9),
                                zero_division=0))

    print("Binary task results (0 is solution is correct, 1 is solution is incorrect):")
    print("(First row human annotation, second predicted)")
    human_binary = [0 if x == 0 else 1 for x in human_labeled_steps]
    predicted_binary = [0 if x == 0 else 1 for x in predicted_error_steps]
    print(human_binary)
    print(predicted_binary)
    print(classification_report(human_binary, predicted_binary, digits=4, zero_division=0))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_id", type=str, default="gpt3_overall_verification",
                        help="Exported output of a model to be evaluated.", )
    args = parser.parse_args()
    output_path = f".{args.model_id}.json"
    evaluate_gsm8k(output_path, args.model_id)
