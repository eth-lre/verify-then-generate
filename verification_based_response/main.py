import argparse
import json
import os

from dataset import MathDial
from apiwrapper import PrompterAPI
from model import ErrorReasonPipeline, ErrorDescriptionPipeline, StepAlignmentPipeline

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="mathdial",
                        help="Dataset to be loaded", choices=['mathdial'])
    parser.add_argument("--model", type=str, default="gpt3",
                        help="Model to use.",
                        choices=['gpt3', 'gpt3-instruct', "llama2_70b_chat", "llama2_70b", "llama3_70b_chat",
                                 "llama3_70b"])
    parser.add_argument("--settings", type=str, default="two_step",
                        help="Settings. "
                             "Baseline is directly generating answer, "
                             "jointly generating verification and answer, "
                             "two step where verification and generation are separate steps, "
                             "and two steps with ground truth data (if available).",
                        choices=['baseline', 'joint', "two_step", "ground_truth_two_step"])
    parser.add_argument("--verification_model", type=str, default="error_description",
                        help="Verification model.", choices=["error_reason", "error_description", "step_alignment"])
    parser.add_argument("--output_dir", type=str, default=".",
                        help="Output directory for the generations.")
    parser.add_argument("--top_n_only", type=int, default=2,
                        help="First n examples in the dataset to run on.")
    parser.add_argument("--debug", type=bool, default=True)
    args = parser.parse_args()

    dataset = MathDial(path="../dataset/dataset.json")
    print(f"Dataset number of data points: {len(dataset.data)}")
    print(dataset.data[:1])

    prompter = PrompterAPI(model=args.model, debug=args.debug)
    tutoring_pipeline = None
    if args.verification_model == "error_reason":
        tutoring_pipeline = ErrorReasonPipeline(prompter, dataset.name, args.verification_model)
    elif args.verification_model == "error_description":
        tutoring_pipeline = ErrorDescriptionPipeline(prompter, dataset.name, args.verification_model)
    elif args.verification_model == "step_alignment":
        tutoring_pipeline = StepAlignmentPipeline(prompter, dataset.name, args.verification_model)

    results = []
    print(f"Final dataset size: {len(dataset.data)}")
    for example in dataset.data[:args.top_n_only]:
        result = ""
        if args.settings == "baseline":
            result = tutoring_pipeline.get_baseline_response(example)
        elif args.settings == "joint":
            result = tutoring_pipeline.get_joint_response(example)
        elif args.settings == "two_step":
            result = tutoring_pipeline.get_two_step_response(example, use_oracle=False)
        elif args.settings == "ground_truth_two_step":
            result = tutoring_pipeline.get_two_step_response(example, use_oracle=True)
        results.append({**example, **result})

    # Rewrite after each example
    EXPORT_PATH = os.path.join(args.output_dir,
                               str(args.dataset) + "_" + str(args.model) + "_" + str(args.verification_model) + "_" + str(
                                   args.settings) + ".json")
    with open(EXPORT_PATH, "w") as outfile:
        outfile.write(json.dumps(results, ensure_ascii=False))
    print(EXPORT_PATH)
