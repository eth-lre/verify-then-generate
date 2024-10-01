import random
from typing import List

import numpy as np
from simcse import SimCSE
from sklearn.metrics.pairwise import cosine_similarity
import re


class StepAlignment(object):
    def __init__(self, model='sbert', similarity_threshold=0.8, gap_utility=0.5, random_seed=42):
        random.seed(random_seed)
        np.random.seed(random_seed)
        self.similarity_threshold = similarity_threshold
        self.gap_utility = gap_utility
        if 'sbert' in model:
            self.model = SimCSE('sentence-transformers/stsb-mpnet-base-v2')
        elif 'roscoe' in model:
            self.model = SimCSE('facebook/roscoe-512-roberta-base')
        elif 'vanilla' in model:
            self.model = model
        elif 'random' in model:
            self.model = model
        else:
            raise ValueError('Aligner Model {} not supported'.format(model))

    def align(self, sequence1: List[str], sequence2: List[str]) -> tuple:
        similarity_scores = self.get_similarities(sequence1, sequence2)
        return self._find_optimal_alignment(sequence1, sequence2, similarity_scores)

    def get_similarities(self, sequence1: List[str], sequence2: List[str]) -> np.ndarray:
        if self.model == "vanilla":
            scores = []
            # for each step in trajectory1, extract all numbers and compare whether the last one is in any step in trajectory2
            for i, step in enumerate(sequence1):
                # extract all numbers from the step
                numbers = re.findall(r'\d+', step)
                if numbers:
                    last_number = numbers[-1]
                    for j, step2 in enumerate(sequence2):
                        if last_number in step2:
                            scores.append(1)
                        else:
                            scores.append(0)
                else:
                    for _, _ in enumerate(sequence2):
                        scores.append(0)
            scores_reshaped = np.array(scores).reshape(len(sequence1), len(sequence2))
            # print(scores_reshaped)
            assert scores_reshaped.shape == (len(sequence1), len(sequence2))
            return scores_reshaped
        elif self.model == "random":
            scores = np.random.rand(len(sequence1), len(sequence2))
            assert scores.shape == (len(sequence1), len(sequence2))
            return scores

        # Embedding cosine similarity
        sequence1_embeddings = self.model.encode(sequence1)
        sequence2_embeddings = self.model.encode(sequence2)
        scores = cosine_similarity(sequence1_embeddings, sequence2_embeddings)
        assert scores.shape == (len(sequence1), len(sequence2))
        return scores

    def _find_optimal_alignment(self, sequence1: List[str], sequence2: List[str],
                                similarity_matrix: np.ndarray) -> tuple:
        m, n = similarity_matrix.shape
        assert len(sequence1) == m and len(sequence2) == n, \
            "Length of sequence1 and sequence2 must match dimensions of sim."

        # Initialize matrices
        # 0: diagonal, 1: up, 2: left
        backtracking_table = np.zeros((m + 1, n + 1), dtype=int)
        scores = np.zeros((m + 1, n + 1), dtype=float)
        for i in range(m + 1):
            scores[i][0] = i * -self.gap_utility
            backtracking_table[i][0] = 1  # From up
        for j in range(n + 1):
            scores[0][j] = j * -self.gap_utility
            backtracking_table[0][j] = 2  # From left

        # Fill the scores based on the matches and similarities
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                # Exact match
                if similarity_matrix[i - 1][j - 1] >= self.similarity_threshold:
                    scores[i][j] += similarity_matrix[i - 1][j - 1]
                    backtracking_table[i][j] = 0
                # Near match or gap
                else:
                    choices = [
                        scores[i - 1][j - 1] - 1 + similarity_matrix[i - 1][j - 1],  # Diagonal
                        scores[i - 1][j] - self.gap_utility,  # Up
                        scores[i][j - 1] - self.gap_utility  # Left
                    ]
                    scores[i][j] = max(choices)
                    backtracking_table[i][j] = choices.index(scores[i][j])

        # Backtracking to find the optimal alignment path
        i, j = m, n
        x_aligned, y_aligned = [], []
        while i > 0 or j > 0:
            if backtracking_table[i][j] == 0:  # Diagonal
                x_aligned.append(sequence1[i - 1])
                y_aligned.append(sequence2[j - 1])
                i -= 1
                j -= 1
            elif backtracking_table[i][j] == 1:  # Up
                x_aligned.append(sequence1[i - 1])
                y_aligned.append('_')
                i -= 1
            elif backtracking_table[i][j] == 2:  # Left
                x_aligned.append('_')
                y_aligned.append(sequence2[j - 1])
                j -= 1

        # Reverse the alignments as we've built them backwards
        x_aligned.reverse()
        y_aligned.reverse()

        return x_aligned, y_aligned, scores[m][n]
