# Stepwise Verification and Remediation of Student Reasoning Errors with Large Language Model Tutors
[![Arxiv](https://img.shields.io/badge/Arxiv-2407.09136-red?style=flat-square&logo=arxiv&logoColor=white)](https://arxiv.org/pdf/2407.09136)
[![License](https://img.shields.io/github/license/UKPLab/ukp-project-template)](https://creativecommons.org/licenses/by/4.0/deed.en)
[![Python Versions](https://img.shields.io/badge/Python-3.10-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)

This repository contains dataset and code for the paper **"Stepwise Verification and Remediation of Student Reasoning Errors with Large Language Model Tutors"**.

*Abstract:*
Large language models (LLMs) present an opportunity to scale high-quality personalized education to all. A promising approach towards this means is to build dialog tutoring models that scaffold students' problem-solving. However, even though existing LLMs perform well in solving reasoning questions, they struggle to precisely detect student's errors and tailor their feedback to these errors. Inspired by real-world teaching practice where teachers identify student errors and customize their response based on them, we focus on verifying student solutions and show how grounding to such verification improves the overall quality of tutor response generation. We collect a dataset of 1K stepwise math reasoning chains with the first error step annotated by teachers. We show empirically that finding the mistake in a student solution is challenging for current models. We propose and evaluate several verifiers for detecting these errors.
Using both automatic and human evaluation we show that the student solution verifiers steer the generation model towards highly targeted responses to student errors which are more often correct with less hallucinations compared to existing baselines.

Contact Persons: [Nico Daheim](https://ndaheim.github.io/), [Jakub Macina](https://macina.sk/)

[ETH-LRE](https://lre.inf.ethz.ch/) | [ETH Zurich](https://ethz.ch/en.html) | [UKP Lab](https://www.ukp.tu-darmstadt.de/) | [TU Darmstadt](https://www.tu-darmstadt.de/
)

![Main Figure](figure1.png)

## Getting Started

The code will be uploaded soon. Once uploaded, it will be possible to install all requirements by using: 
  ```
  pip install -r requirements.txt
  ```

## Dataset
The dataset will be uploaded to the folder `dataset` shortly. The dataset is an extension of [MathDial](https://github.com/eth-nlped/mathdial) and contains 1k student solutions and their stepwise reasoning chains in the domain of multi-step math problem-solving.

The structure of the dataset is:
- *problem*: Question student is solving.
- *topic*: Short lesson topic description.
- *reference_solution*: Solution to the problem.
- *incorrect solution*: Student incorrect solution.
- *incorrect_step*: The first step with a student mistake as annotated by a teacher.
- *error_category*: Category of the error.
- *error_description*: Description of the error annotated by a teacher. 
- *dialog_history*: Dialogue between teacher and student. The student explains their solution as a part of their response.


Example:
```json
{
        "problem": "Carl has been selling watermelons on the side of the road for $3 each. This evening he went home with $105 in profit and 18 watermelons. How many watermelons did he start out with this morning?",
        "topic": "Math Word Problem",
        "reference_solution": "Carl sells his watermelons for $3 each so today he sold $105 / $3 per watermelon = 35 watermelons.\nHe had 18 watermelons left over, so this morning he started with 18 + 35 = 53 watermelons.\n 53",
        "incorrect_solution": [
            "Let's start by finding out how much money Carl made selling the 18 watermelons. Since he sold each watermelon for $3, he made 18 x $3 = $54.",
            "We know that his total profit for the day was $105, so he must have started with $105 - $54 = $51 worth of watermelons.",
            "Since each watermelon costs $3, he must have started with 51 / $3 = 17 watermelons.",
            " 17"
        ],
        "incorrect_step": "Let's start by finding out how much money Carl made selling the 18 watermelons. Since he sold each watermelon for $3, he made 18 x $3 = $54.",
        "error_category": "Misunderstanding of a question",
        "error_description": "Carl did not sell 18 watermelons, but 18 watermelons are left unsold.",
        "dialog_history": [
            {
                "text": "hi deandre, talk me through your solution",
                "user": "Teacher"
            },
            {
                "text": "DeAndre: Hi, I started by finding out how much money Carl made selling the 18 watermelons. Since he sold each watermelon for $3, he made 18 x $3 = $54. Then I realized that his total profit for the day was $105, so he must have started with $105 - $54 = $51 worth of watermelons. Since each watermelon costs $3, I concluded that he must have started with 51 / $3 = 17 watermelons.",
                "user": "Student"
            },
            {
                "text": "how much did the watermelons cost and how much money did he come home with?",
                "user": "Teacher"
            }
        ],        
...
}
```

## Evaluation
A detailed guide for evaluating various models will be published soon along the code.

## Citation
Please cite as:
```
Bibtex will be added shortly.
```

## Disclaimer
This repository contains experimental software and data and is published for the purpose of giving additional background details on the respective publication.
