import argparse
import json
import os
import re
import time
from typing import List

import openai

TARGETEDNESS = """You are a Critic giving feedback on the Teacher's tutoring skills. As the Critic you assess whether the Teacher points out the root cause of the Student's mistake.
Answer 'No' if the Student's statement is wrong and the Teacher does not point out the mistake directly. Answer 'No' if the Teacher gives the right answer without pointing out the mistake. Answer 'Yes' if the Teacher correctly describes the mistake in the student's solution. Answer 'No' if the Teacher addresses the correct part of the student solution. Answer 'No' if response is too general and could be applied to any mistake e.g. 'You made a small mistake'.
Does the Teacher points out to the root cause of the student's mistake?  Output a 'Yes' or 'No' decision and a short rationale in the format Decision: <decision>. Rationale: <rationale>.

[Examples]
Problem: The profit from a business transaction is shared among 2 business partners, Mike and Johnson in the ratio 2:5 respectively. If Johnson got $2500, how much will Mike have after spending some of his share on a shirt that costs $200?
Solution: According to the ratio, for every 5 parts that Johnson gets, Mike gets 2 parts. Since Johnson got $2500, each part is therefore $2500/5 = $500. Mike will get 2*$500 = $1000. After buying the shirt he will have $1000-$200 = $800 left
[Dialogue]
Teacher: Could you please walk me through your solution?
Student: Sure. I figured that Jonsons' profit of $2500 is equivalent to 7 parts, so each part is worth $357.14. Since Mike got 2 parts, his total portion is 714.28, of which he spent 200, leaving him with 514.28

[Example 1]
Teacher response: Great job on correctly calculating the value of each part and determining Mike's remaining amount after spending on the shirt. Your final answer is correct.
Request: Does the Teacher point out the root cause of the student's mistake? 
Critic: Decision: No. Rationale: The teacher does not identify any error in the student's solution. Moreover, it acknowledges the student's incorrect solution as correct.

[Example 2]
Teacher response: Your calculation is incorrect. Can you try to double-check the parts each gets?
Request: Does the Teacher point out the root cause of the student's mistake? 
Critic: Decision: No. Rationale: The teacher just generally state your solution is incorrect and this is not specific to the student error.

[Example 3]
Teacher response: Johnson's $2500 represents 5 parts, not 7, so each part is $500, and Mike's share before buying the shirt is $1000, not $714.28. So the solution is $800.
Request: Does the Teacher point out the root cause of the student's mistake? 
Critic: Decision: Yes. Rationale: The Teacher provides very specific identification by directly stating the problem is in using the wrong number of parts.
[The End of Examples]

Problem: ${problem}
Correct Solution: ${correct_answer}
[Dialogue]
${dialogue_history}
Teacher response: ${response}
Request: Does the Teacher point out the root cause of the student's mistake? 
Critic:"""

CORRECTNESS = """You are a Critic giving feedback on the correctness of the Teacher who is interacting with a Student. 
The teacher should NOT say incorrect information or provide parts of the solution that are NOT correct with respect to the Correct Solution. 
Answer 'No' if the Teacher provides parts of a solution that is incorrect or does not guide a student towards the Correct Solution.
Is the Teacher's response factually correct with respect to the correct solution? Output a 'Yes' or 'No' decision and a short rationale in the format Decision: <decision>. Rationale: <rationale>.
Carefully compare the Correct Solution and the Teacher's response.

[Examples]
Problem: The profit from a business transaction is shared among 2 business partners, Mike and Johnson in the ratio 2:5 respectively. If Johnson got $2500, how much will Mike have after spending some of his share on a shirt that costs $200?
Solution: According to the ratio, for every 5 parts that Johnson gets, Mike gets 2 parts. Since Johnson got $2500, each part is therefore $2500/5 = $500. Mike will get 2*$500 = $1000. After buying the shirt he will have $1000-$200 = $800 left
[Dialogue]
Teacher: Could you please walk me through your solution?
Student: Sure. I figured that Jonsons' profit of $2500 is equivalent to 7 parts, so each part is worth $357.14. Since Mike got 2 parts, his total portion is 714.28, of which he spent 200, leaving him with 514.28

[Example 1]
Teacher response: Your calculation is incorrect. Can you try to double-check the parts each gets?
Request: Is the Teacher's response factually correct with respect to the correct solution?
Critic: Decision: Yes. Rationale: The Teacher's response correctly states there is a mistake in the student's calculation and ask a question. Nothing factually incorrect is said.

[Example 2]
Teacher response: Johnson's $2500 represents 5 parts, not 7, so each part is $500, and Mike's share before buying the shirt is $1000, not $714.28. So the solution is $800.
Request: Is the Teacher's response factually correct with respect to the correct solution?
Critic: Decision: Yes. Rationale: The Teacher's response is stating part of the correct solution and it is factually correct.

[Example 3]
Teacher response: Great job on correctly calculating the value of each part and determining Mike's remaining amount after spending on the shirt. Your final answer is correct.
Request: Is the Teacher's response factually correct with respect to the correct solution?
Critic: Decision: No. Rationale: The Teacher acknowledges the student's incorrect solution as correct, which is not factually correct given the correct answer.
[The End of Examples]

Problem: ${problem}
Correct Solution: ${correct_answer}
[Dialogue]
${dialogue_history}
Teacher response: ${response}
Request: Is the Teacher's response factually correct with respect to the correct solution?
Critic:"""

ACTIONABLE = """You are a Critic giving feedback on the responses of the Teacher who is interacting with a Student. 
Your task is to gauge if the Teacher's Response provides actionable hints or steps without revealing the full solution.
The Student could use this response to move closer to the final correct answer. 
A good response could also be a follow-up question that makes the user think about how to solve the problem.
Does the Teacher provide actionable steps without giving away the full answer? Output a 'Yes' or 'No' decision and a short rationale in the format Decision: <decision>. Rationale: <rationale>.
Answer 'No' if the Teacher simply just reveals the full Correct Solution.

[Examples]
Problem: The profit from a business transaction is shared among 2 business partners, Mike and Johnson in the ratio 2:5 respectively. If Johnson got $2500, how much will Mike have after spending some of his share on a shirt that costs $200?
Solution: According to the ratio, for every 5 parts that Johnson gets, Mike gets 2 parts. Since Johnson got $2500, each part is therefore $2500/5 = $500. Mike will get 2*$500 = $1000. After buying the shirt he will have $1000-$200 = $800 left
[Dialogue]
Teacher: Could you please walk me through your solution?
Student: Sure. I figured that Jonsons' profit of $2500 is equivalent to 7 parts, so each part is worth $357.14. Since Mike got 2 parts, his total portion is 714.28, of which he spent 200, leaving him with 514.28

[Example 1]
Teacher response: Your calculation is incorrect. Can you try to double-check the parts each gets?
Request: Does the Teacher provide actionable steps without giving away the full answer?
Critic: Decision: Yes. Rationale: the teacher asks a question or ask for action from the student to double-check the answer.

[Example 2]
Teacher response: Johnson's $2500 represents 5 parts, not 7, so each part is $500, and Mike's share before buying the shirt is $1000, not $714.28. So the solution is $800.
Request: Does the Teacher provide actionable steps without giving away the full answer?
Critic: Decision: No. Rationale: The teacher states the correct solution at the end.

[Example 3]
Teacher response: Johnson's $2500 represents 5 parts, not 7, so each part is $500, and Mike's share before buying the shirt is $1000, not $714.28. 
Request: Does the Teacher provide actionable steps without giving away the full answer?
Critic: Decision: Yes. Rationale: The teacher points out what is wrong with the student's solution but do not tell the full correct answer.
[The End of Examples]

Problem: ${problem}
Correct Solution: ${correct_answer}
[Dialogue]
${dialogue_history}
Teacher response: ${response}
Request: Does the Teacher provide actionable steps without giving away the full answer?
Critic:"""


def grade(prompt_to_use: str, grader_model: str, model_output: str, response_key: str):
    is_predicted_correct = False
    rationale = ""

    if "llama" in grader_model:
        openai.api_key = "EMPTY"
        openai.api_base = "http://localhost:8000/v1"

    teacher_response = model_output[response_key]
    if isinstance(model_output.get(response_key), list):
        teacher_response = model_output[response_key][0]["text"]

    prompt = (prompt_to_use.replace("${dialogue_history}", "\n".join(
        [turn["user"] + ": " + turn["text"] for turn in model_output["dialog_history"]]))
              .replace("${response}",
                       teacher_response)  # ["ground_truth_responses"][0]["text"]) # model_output["response"]
              .replace("${correct_answer}", model_output["reference_solution"].replace("\n", "\\n")).replace(
        "${problem}", model_output["problem"]))
    no_answer = True
    messages = [{"role": "system", "content": prompt}]
    while no_answer:
        try:
            response = openai.ChatCompletion.create(
                model=grader_model,
                messages=messages,
                max_tokens=60,
                temperature=0
            )
            no_answer = False

            output = response.choices[0]["message"]["content"]
            print("=====================================")
            print(prompt)
            print(output)
            print("=====================================")

            decision_part = output.split("ationale:")[0]

            is_predicted_correct = False
            if re.findall(r'Decision: NO', decision_part, re.IGNORECASE):
                is_predicted_correct = False
            elif re.findall(r'Decision: YES', decision_part, re.IGNORECASE):
                is_predicted_correct = True
            else:
                print("ISSUE: no YES/NO found in the response")
                is_predicted_correct = False
                output += "REMOVE: no YES/NO found in the response"

            rationale = output
            # rationale = output.split("ationale:")
        except Exception as e:
            print(f"Retry because of {e}")
            time.sleep(1)

    print(f"Parsed decision: {is_predicted_correct}, Rationale: {rationale}")
    return is_predicted_correct, rationale


def compute_results(evaluations: List[bool]) -> float:
    return sum(evaluations) / len(evaluations)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_outputs_json", default="mathdial_gpt3_step_alignment_two_step.json",
                        help="Model outputs.")
    parser.add_argument("--response_key", default="response", help="Key for the response")
    parser.add_argument("--grader", default="gpt4",
                        choices=["gpt4", "llama3"],
                        help="API model for critic")
    parser.add_argument("--top_n_only", type=int, default=2,
                        help="First n examples in the dataset to run on.")
    parser.add_argument("--output_dir", type=str, default=".",
                        help="Output directory for the generations.")
    args = parser.parse_args()

    grader_model = ""
    if "llama3" in args.grader:
        grader_model = "meta-llama/Meta-Llama-3-70B-Instruct"
    elif "gpt4" in args.grader:
        grader_model = "gpt-4-0125-preview"
    else:
        print("Unknown grader model")
        exit(1)

    with open("." + args.model_outputs_json, "r", encoding="utf-8") as f:
        model_outputs = json.load(f)

    print(f"Grading {args.model_outputs_json}.")
    targeted, correctness, actionable = [], [], []
    targed_explanations, correctness_explanations, actionable_explanations = [], [], []
    for model_output in model_outputs[:args.top_n_only]:
        target_value, targed_explanation = grade(TARGETEDNESS, grader_model, model_output, args.response_key)
        correctness_value, correctness_explanation = grade(CORRECTNESS, grader_model, model_output, args.response_key)
        actionable_value, actionable_explanation = grade(ACTIONABLE, grader_model, model_output, args.response_key)
        targeted.append(target_value)
        targed_explanations.append(targed_explanation)
        correctness.append(correctness_value)
        correctness_explanations.append(correctness_explanation)
        actionable.append(actionable_value)
        actionable_explanations.append(actionable_explanation)

    targeted_score = compute_results(targeted)
    print(f"{args.model_outputs_json} targeted score: {targeted_score * 100}")
    correctness_score = compute_results(correctness)
    print(f"{args.model_outputs_json} correctness score: {correctness_score * 100}")
    actionable_score = compute_results(actionable)
    print(f"{args.model_outputs_json} actionable score: {actionable_score * 100}")

    to_output = [{
        "history": [turn["user"] + ": " + turn["text"] for turn in model["dialog_history"]],
        "model": model[args.response_key] if not isinstance(model[args.response_key], list) else
        model[args.response_key][0]["text"],
        "solution": model["reference_solution"],
        "targeted": targetedness,
        "targeted_explanation": targed_explanation,
        "correctness": correctness,
        "correctness_explanation": correctness_explanation,
        "actionable": actionable,
        "actionable_explanation": actionable_explanation,
    } for
        model, targetedness, targed_explanation, correctness, correctness_explanation, actionable, actionable_explanation
        in zip(model_outputs, targeted, targed_explanations, correctness, correctness_explanations, actionable,
               actionable_explanations)]
    EXPORT_PATH = os.path.join(args.output_dir,
                               "criticgrade-" + args.grader + "-" + args.response_key + "-" + args.model_outputs_json)
    with open(EXPORT_PATH, 'w') as file:
        json.dump(to_output, file, indent=4)
    print("Exported judgments to:", EXPORT_PATH)
