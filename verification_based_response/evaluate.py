import argparse
import json
from typing import List

import nltk
import numpy as np
from sacrebleu.metrics import BLEU
from sentence_transformers import SentenceTransformer, util
from bert_score import score
from collections import Counter
from nltk.tokenize import RegexpTokenizer

tokenizer = RegexpTokenizer(r'\w+')


def compute_corpus_bleu(ground_truths: List[str], predictions: List[str]):
    assert len(ground_truths) == len(predictions)
    list_of_target_token_list, list_of_pred_token_list = [], []
    for k in range(len(ground_truths)):
        one_target_token_list = ground_truths[k].strip().split()
        list_of_target_token_list.append(one_target_token_list)
        one_pred_token_list = predictions[k].strip().split()
        list_of_pred_token_list.append(one_pred_token_list)

    list_of_references, list_of_hypotheses = [], []
    for k in range(len(list_of_target_token_list)):
        list_of_references.append([list_of_target_token_list[k]])
        list_of_hypotheses.append(list_of_pred_token_list[k])
    return nltk.translate.bleu_score.corpus_bleu(list_of_references,
                                                 list_of_hypotheses, weights=[(1, 0.0, 0.0, 0.0),
                                                                              (1. / 2., 1. / 2.),
                                                                              (1. / 3., 1. / 3., 1. / 3.),
                                                                              (1. / 4., 1. / 4., 1. / 4., 1. / 4.)])


def compute_bert_score(ground_truths: List[str], predictions: List[str]):
    assert len(ground_truths) == len(predictions)

    # define model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    gt_embeddings = model.encode(ground_truths, convert_to_tensor=True)
    pred_embeddings = model.encode(predictions, convert_to_tensor=True)

    cosine_score = [util.cos_sim(gt_embed, pred_embed).item() for gt_embed, pred_embed in
                    zip(gt_embeddings, pred_embeddings)]
    return (sum(cosine_score) / len(ground_truths)), cosine_score


def simple_count_number_of_questions(text: str) -> int:
    return text.count("?")

def _token_f1(prediction, reference):
    prediction_tokens = tokenizer.tokenize(prediction)
    reference_tokens = tokenizer.tokenize(reference)

    common = Counter(prediction_tokens) & Counter(reference_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(reference_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1


def run_evaluation(path: str):
    with open(path, "r", encoding="utf-8") as f:
        raw_predictions = json.load(f)

    all_gt = [item["dialog_history"][0]["text"] for item in raw_predictions]
    all_pred = [prediction["response"] for prediction in raw_predictions]
    all_knowledge = [prediction["reference_solution"] for prediction in raw_predictions]

    print(len(all_pred))
    print(all_gt[:2])
    print(all_pred[:2])

    sentence_bleu = []
    for sample_gt, sample_pred in zip(all_gt, all_pred):
        reference = [ref.strip().split() for ref in sample_gt]
        hypothesis = sample_pred.strip().split()
        BLEUscore = nltk.translate.bleu_score.sentence_bleu(reference, hypothesis,
                                                            weights=[(1, 0.0, 0.0, 0.0),
                                                                     (1. / 2., 1. / 2.),
                                                                     (1. / 3., 1. / 3., 1. / 3.),
                                                                     (1. / 4., 1. / 4., 1. / 4., 1. / 4.)])
        sentence_bleu.append(BLEUscore)

    sentence_bleu = np.array(sentence_bleu)
    print(f"Overall sentence BLUE score: {np.average(sentence_bleu, axis=0) * 100}")

    corpus_bleu = compute_corpus_bleu(all_gt, all_pred)
    print(f"Overall corpus BLUE score: {corpus_bleu * np.array([100, 100, 100, 100])}")

    overall_bert_score, bert_score = compute_bert_score(all_gt, all_pred)
    print(f"Overall BERT score: {overall_bert_score}")

    sacre_bleu = BLEU()
    sacrebleu_scores = sacre_bleu.corpus_score(all_pred, [all_gt]).format(width=6)
    print(f"Sacrebleu results: {sacrebleu_scores}")
    print(sacre_bleu.get_signature())

    bert_scores = score(all_pred, all_gt, lang="en", model_type="microsoft/deberta-large-mnli", verbose=False)
    P, R, f1 = (tensor.mean().item() for tensor in bert_scores)
    print(f"System level F1 score: {f1:.6f}, P: {P:.6f}, R: {R:.6f}")

    # Compute token-level F1
    token_f1 = [_token_f1(pred, ref) for pred, ref in zip(all_pred, all_knowledge)]
    print(f"Token-level F1: {np.mean(token_f1):.6f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_outputs_json", type=str,
                        default="mathdial_gpt3_step_alignment_two_step.json",
                        help="Exported output of a model to be evaluated.", )
    args = parser.parse_args()
    print("Loading model outputs from:", args.model_outputs_json)
    run_evaluation(args.model_outputs_json)
