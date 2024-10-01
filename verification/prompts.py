OVERALL_VERIFICATION = """You are an experienced math teacher. Your goal is to identify the correctness of the Student's Solution to a Problem.

Problem: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?
Student Solution: I started by calculating clips in May which is 48/2 = 24. Then I sum this up, so she sold 48+24 = 72 clips in April and May together.
Q: Is the Student Solution incorrect? Write "Yes" if it is incorrect, or "No" if it is correct.
A: No

Problem: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?
Student Solution: Sure. We know Natalia sold 48 clips in April. She sold 48*2 = 96 clips in May. To compute for two months, I simply sum it up, so 48+96 = 144 clips in April and May together.
Is the Student Solution incorrect? Write "Yes" if it is incorrect, or "No" if it is correct.A: Yes

Problem: {QUESTION}
Student Solution: {STUDENT_ANSWER}
Is the Student Solution incorrect? Write "Yes" if it is incorrect, or "No" if it is correct.
A: """

OVERALL_VERIFICATION_WITH_SOLUTION = """You are an experienced math teacher. Your goal is to identify the correctness of the Student's Solution to a Problem.

Problem: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?
Expected Answer: Natalia sold 48/2 = <<48/2=24>>24 clips in May. Natalia sold 48+24 = <<48+24=72>>72 clips altogether in April and May.
Student Solution: I started by calculating clips in May which is 48/2 = 24. Then I sum this up, so she sold 48+24 = 72 clips in April and May together.
Q: Is the Student Solution incorrect? Write "Yes" if it is incorrect, or "No" if it is correct.
A: No

Problem: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?
Expected Answer: Natalia sold 48/2 = <<48/2=24>>24 clips in May. Natalia sold 48+24 = <<48+24=72>>72 clips altogether in April and May.
Student Solution: Sure. We know Natalia sold 48 clips in April. She sold 48*2 = 96 clips in May. To compute for two months, I simply sum it up, so 48+96 = 144 clips in April and May together.
Q: Is the Student Solution incorrect? Write "Yes" if it is incorrect, or "No" if it is correct.
A: Yes

Problem: {QUESTION}
Expected Answer: {CORRECT_ANSWER}
Student Solution: {STUDENT_ANSWER}
Q: Is the Student Solution incorrect? Write "Yes" if it is incorrect, or "No" if it is correct.
A: """

STEPWISE_VERIFICATION_WITH_SOLUTION = """You are an experienced math teacher. Your goal is to identify the step of the first mistake in the Student's Solution to a Problem.

Problem: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?
Expected Answer: Step 1 - Natalia sold 48/2 = <<48/2=24>>24 clips in May.\\nStep 2 - Natalia sold 48+24 = <<48+24=72>>72 clips altogether in April and May.
Student Solution: Step 1 - She sold 48/2 = 24 clips in May.\\nStep 2 - Natalia sold 48+24 = 72 clips in April and May together.
Q: Is the Student Solution incorrect? Write only the step number with the first error or 0 if no error is found.
A: 0

Problem: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?
Expected Answer: Step 1 - Natalia sold 48/2 = <<48/2=24>>24 clips in May.\\nStep 2 - Natalia sold 48+24 = <<48+24=72>>72 clips altogether in April and May.
Student Solution: Step 1 - Natalia sold 48 clips in April.\\nStep 2 - She sold 48*2 = 96 clips in May.\\nStep 3 - She sold 48+96 = 144 clips in April and May together.
Q: Is the Student Solution incorrect? Write only the step number with the first error or 0 if no error is found.
A: 2

Problem: {QUESTION}
Expected Answer: {CORRECT_ANSWER}
Student Solution: {STUDENT_ANSWER}
Q: Is the Student Solution incorrect? Write only the step number with the first error or 0 if no error is found.
A: """

STEPWISE_VERIFICATION = """You are an experienced math teacher. Your goal is to identify the step of the first mistake in the Student's Solution to a Problem.

Problem: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?
Student Solution:Step 1 - She sold 48/2 = 24 clips in May.\\nStep 2 - Natalia sold 48+24 = 72 clips in April and May together.
Q: Is the Student Solution incorrect? Write only the step number with the first error or 0 if no error is found.
A: 0

Problem: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?
Student Solution:Step 1 - Natalia sold 48 clips in April.\\nStep 2 - She sold 48*2 = 96 clips in May.\\nStep 3 - She sold 48+96 = 144 clips in April and May together.
Q: Is the Student Solution incorrect? Write only the step number with the first error or 0 if no error is found.
A: 2

Problem: {QUESTION}
Student Solution:{STUDENT_ANSWER}
Q: Is the Student Solution incorrect? Write only the step number with the first error or 0 if no error is found.
A: """

PROMPTS = {
    "overall_verification_with_solution": {
        "name": "overall_verification_with_solution",
        "version": "1.0",
        "prompt": OVERALL_VERIFICATION_WITH_SOLUTION
    },
    "overall_verification": {
        "name": "overall_verification",
        "version": "1.0",
        "prompt": OVERALL_VERIFICATION
    },
    "stepwise_verification_with_solution": {
        "name": "stepwise_verification_with_solution",
        "version": "1.0",
        "prompt": STEPWISE_VERIFICATION_WITH_SOLUTION
    },
    "stepwise_verification": {
        "name": "stepwise_verification",
        "version": "1.0",
        "prompt": STEPWISE_VERIFICATION
    },
}
