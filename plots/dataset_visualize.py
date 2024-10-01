import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter

if __name__ == '__main__':
    DATASET_PATH = "../dataset/dataset.json"
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    ground_truth_steps = [len(entry['reference_solution'].split('\n')) for entry in data]
    total_steps = [len(entry['student_incorrect_solution']) for entry in data]
    error_lines = [entry['incorrect_index'] + 1 for entry in data]

    print(Counter(error_lines))
    print(Counter(total_steps))

    sns.set_style("whitegrid")
    sns.set_palette("colorblind")
    sns.set_context("paper", font_scale=1.5, rc={"lines.linewidth": 3.5})

    max_steps = max(total_steps)
    bins = range(0, max_steps + 1)
    fig, ax = plt.subplots(figsize=(14, 10))

    sns.histplot(error_lines, bins=bins, kde=False, color='lightseagreen', ax=ax, discrete=True,
                 label='Step with Error', hatch='', edgecolor='black')
    sns.histplot(total_steps, bins=bins, kde=False, color='indianred', ax=ax, discrete=True,
                 label='Total Student Solution Steps', hatch='/', edgecolor='black')

    ax.set_xlabel('Step', fontsize=22)
    ax.set_ylabel('Frequency', fontsize=22)
    ax.set_xticks(range(0, max_steps + 1))
    ax.set_xticklabels(ax.get_xticks(), fontsize=22)
    y_ticks = ax.get_yticks()
    ax.set_yticklabels([int(y) for y in y_ticks], fontsize=22)
    ax.grid(True, linestyle='--', linewidth=0.7)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.10), ncol=2, fontsize=22)  # Increase font size

    mean_error_lines = np.mean(error_lines)
    mean_total_steps = np.mean(total_steps)
    ax.axvline(mean_error_lines, color='navy', linestyle='--', linewidth=3)
    ax.axvline(mean_total_steps, color='maroon', linestyle='--', linewidth=3)
    ax.text(mean_error_lines, ax.get_ylim()[1] * 0.9, f'Mean Error Step: {mean_error_lines:.2f}', color='blue',
            fontsize=22, ha='right')
    ax.text(mean_total_steps, ax.get_ylim()[1] * 0.7, f'Mean Total Steps: {mean_total_steps:.2f}', color='red',
            fontsize=22, ha='left')

    ax.grid(axis='y', linestyle='--', linewidth=2, color='gray', alpha=0.5)
    ax.grid(axis='x', linestyle='--', linewidth=2.5, color='gray', alpha=0)
    ax.set_xlim(bins[0], bins[-1]+0.50)

    plt.tight_layout()
    plt.savefig('dataset-error-step.pdf', format='pdf', dpi=1000, bbox_inches='tight')
    plt.show()
