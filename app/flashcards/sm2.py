"""
SM2 Algorithm Implementation
"""


def sm2(grade, old_ease_factor, old_interval, old_repetition):
    """
    Apply SM2 algorithm to update scheduling
    fields based on user's recall grade.
    grade: int (0-5)
    old_ease_factor: Decimal or float
    old_interval: int (days)
    old_repetition: int
    Returns: (new_ease_factor, new_interval, new_repetition)
    """
    # Minimum ease factor is 1.3 (per SuperMemo)
    MIN_EF = 1.3

    if grade < 3:
        # Again, soon!
        return (max(old_ease_factor - 0.2, MIN_EF), 1, 0)

    # Repetition successful
    new_repetition = old_repetition + 1

    # First/second correct reviews: intervals 1, 6, then calculated
    if new_repetition == 1:
        new_interval = 1
    elif new_repetition == 2:
        new_interval = 6
    else:
        new_interval = int(old_interval * old_ease_factor)

    # Update ease factor
    new_ease_factor = (old_ease_factor +
                       (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
                       )
    new_ease_factor = max(new_ease_factor, MIN_EF)

    return (new_ease_factor, new_interval, new_repetition)
