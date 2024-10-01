# Baseline - direct generation without verification
DIRECT_GENERATION = """You are an experienced teacher and you are going to respond to a student. The problem your student is solving is on topic: ${lesson_topic}.
Problem: ${problem}

[conversation]
Teacher (maximum two sentences):"""

#### Verification step - Baseline from Bridge
VERIFY_REMATH_BASELINE = """You are an experienced elementary math teacher. Your task is to read a conversation snippet of a tutoring session between a student and tutor, and determine what type of error the student makes in the conversation. We have a list of common errors that students make in math, which you can pick from. We also give you the option to write in your own error type if none of the options apply.
Error list:
0. Student does not seem to understand or guessed the answer.
1. Student misinterpreted the question.
2. Student made a careless mistake.
3. Student has the right idea, but is not quite there.
4. Student’s answer is not precise enough or the tutor is being too picky about the form
of the student’s answer.
5. None of the above, but I have a different description (please specify in your
reasoning).
6. Not sure, but I’m going to try to diagnose the student.

Here is the conversation snippet:
Lesson topic: ${lesson_topic}
Problem: ${problem}
Conversation:

[conversation]

Why do you think the student made this mistake? Pick an option number from the error list and provide the reason behind your choice. Format your answer as: {"answer": #, "reason": "write out your reason for picking # here"}
"""

# Verification step - Error description
VERIFY_STEP_ERROR_DESCRIPTION = """You are an experienced math teacher. Your goal is to identify the correctness of the Student's Solution to a Problem.

Problem: ${problem}
Expected correct solution: ${solution}
[conversation]
Q: Find the first error in the student solution compared to the expected correct solution and write a one line description. If no error, write "Student' solution is Correct".
A:"""

# Generation step
GENERATE_AFTER_VERIFICATION = """You are an experienced teacher and you are going to respond to a student. The problem your student is solving is on topic: ${lesson_topic}.
Problem: ${problem}
Assessment of student solution: ${assessment}

[conversation]
Teacher (maximum two sentences):"""

# CoT solution
COT_SOLUTION = """You are a highly intelligent question answering assistant. Solve the question step-by-step. Always finish the answer by providing your final answer after 'The answer is'.
Question: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?
Answer: Natalia sold 48/2 = <<48/2=24>>24 clips in May.\nNatalia sold 48+24 = <<48+24=72>>72 clips altogether in April and May. The answer is 72
Question: Julie is reading a 120-page book. Yesterday, she was able to read 12 pages and today, she read twice as many pages as yesterday. If she wants to read half of the remaining pages tomorrow, how many pages should she read?
Answer: Maila read 12 x 2 = <<12*2=24>>24 pages today.\nSo she was able to read a total of 12 + 24 = <<12+24=36>>36 pages since yesterday.\nThere are 120 - 36 = <<120-36=84>>84 pages left to be read.\nSince she wants to read half of the remaining pages tomorrow, then she should read 84/2 = <<84/2=42>>42 pages. The answer is 42
Question: Weng earns $12 an hour for babysitting.Yesterday, she just did 50 minutes of babysitting. How much did she earn?
Answer: Weng earns 12/60 = <<12/60=0.2>>0.2 per minute.\nWorking 50 minutes, she earned 0.2 x 50 = <<0.2*50=10>>10. The answer is 10
Question: The profit from a business transaction is shared among 2 business partners, Mike and Johnson in the ratio 2:5 respectively. If Johnson got $2500, how much will Mike have after spending some of his share on a shirt that costs $200?
Answer: According to the ratio, for every 5 parts that Johnson gets, Mike gets 2 parts\nSince Johnson got $2500, each part is therefore $2500/5 = $<<2500/5=500>>500\nMike will get 2*$500 = $<<2*500=1000>>1000\nAfter buying the shirt he will have $1000-$200 = $<<1000-200=800>>800 left. The answer is 800
Question: Ralph is going to practice playing tennis with a tennis ball machine that shoots out tennis balls for Ralph to hit. He loads up the machine with 175 tennis balls to start with. Out of the first 100 balls, he manages to hit 2/5 of them. Of the next 75 tennis balls, he manages to hit 1/3 of them. Out of all the tennis balls, how many did Ralph not hit?
Answer: Out of the first 100 balls, Ralph was able to hit 2/5 of them and not able to hit 3/5 of them, 3/5 x 100 = 60 tennis balls Ralph didn't hit.\nOut of the next 75 balls, Ralph was able to hit 1/3 of them and not able to hit 2/3 of them, 2/3 x 75 = 50 tennis balls that Ralph didn't hit.\nCombined, Ralph was not able to hit 60 + 50 = <<60+50=110>>110 tennis balls Ralph didn't hit. The answer is 110
Question: ${problem}
Answer:"""