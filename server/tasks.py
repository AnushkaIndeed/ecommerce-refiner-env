def default_grader(submission, target):
    """Standard grader for brand extraction tasks."""
    val = str(submission).upper().strip()
    correct = str(target).upper()

    if val == correct:
        return 0.9
    elif correct in val or val in correct:
        return 0.6
    elif val != "":
        return 0.3
    else:
        return 0.1


TASKS = [
    {
        "difficulty": "easy",
        "input": "NIKE AIR MAX - RED - SIZE 10",
        "target": "NIKE",
        "grader": default_grader
    },
    {
        "difficulty": "medium",
        "input": "Apple green silk dress by Zara",
        "target": "ZARA",
        "grader": default_grader
    },
    {
        "difficulty": "hard",
        "input": "Puma Suede Classic - North Face Edition",
        "target": "PUMA",
        "grader": default_grader
    }
]