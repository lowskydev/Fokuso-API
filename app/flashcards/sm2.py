"""
Anki-like Algorithm Implementation
"""
from decimal import Decimal
from datetime import timedelta


def anki_algorithm(grade, old_ease_factor, old_interval, old_repetition, is_learning=None):
    """
    Apply Anki-like algorithm to update scheduling fields based on
    user's recall grade.
    grade: int (1-4 where 1=Again, 2=Hard, 3=Good, 4=Easy)
    old_ease_factor: int (in percentage, e.g., 250 for 2.5x)
    old_interval: int (in minutes for learning, days for review)
    old_repetition: int
    is_learning: bool (if None, auto-detect based on repetition)
    Returns: (new_ease_factor, new_interval_minutes, new_repetition, is_learning_phase)
    """
    MIN_EF = 130  # 1.3x in percentage form

    # Convert ease factor to percentage if it's in decimal form
    if old_ease_factor < 10:
        old_ease_factor = int(old_ease_factor * 100)

    # Auto-detect learning phase if not specified
    if is_learning is None:
        is_learning = old_repetition < 2

    new_repetition = old_repetition
    new_is_learning = is_learning

    if grade == 1:  # Again
        # Reset to learning phase
        new_repetition = 0
        new_is_learning = True
        new_interval_minutes = 1  # 1 minute (immediate in practice)
        new_ease_factor = max(old_ease_factor - 20, MIN_EF)  # Reduce by 20%

    elif grade == 2:  # Hard
        if is_learning:
            # In learning phase - stay in learning
            new_repetition = old_repetition  # Don't advance repetition
            new_is_learning = True
            new_interval_minutes = 10  # 10 minutes
            new_ease_factor = old_ease_factor  # Don't change ease in learning
        else:
            # In review phase
            new_repetition = old_repetition + 1
            new_is_learning = False
            new_ease_factor = max(old_ease_factor - 15, MIN_EF)  # Reduce by 15%
            # Convert old interval from days to minutes for calculation
            old_interval_days = old_interval if old_interval > 1440 else old_interval / 1440
            new_interval_days = max(1, old_interval_days * 1.2)
            new_interval_minutes = int(new_interval_days * 1440)  # Convert back to minutes

    elif grade == 3:  # Good
        new_repetition = old_repetition + 1
        new_ease_factor = old_ease_factor  # Ease factor stays the same

        if is_learning:
            if new_repetition == 1:
                new_interval_minutes = 10  # 10 minutes
                new_is_learning = True
            elif new_repetition == 2:
                new_interval_minutes = 1440  # 1 day (graduate to review)
                new_is_learning = False
            else:
                # Shouldn't happen in normal learning, but handle it
                new_interval_minutes = 1440  # 1 day
                new_is_learning = False
        else:
            # In review phase
            new_is_learning = False
            # Convert old interval from minutes to days if needed
            old_interval_days = old_interval if old_interval > 1440 else old_interval / 1440
            new_interval_days = old_interval_days * (old_ease_factor / 100)
            new_interval_minutes = int(new_interval_days * 1440)  # Convert to minutes

    elif grade == 4:  # Easy
        new_repetition = old_repetition + 1
        new_ease_factor = old_ease_factor + 15  # Increase by 15%

        if is_learning:
            # Graduate immediately from learning
            new_is_learning = False
            new_interval_minutes = 4 * 1440  # 4 days
        else:
            # In review phase - easier than good
            new_is_learning = False
            old_interval_days = old_interval if old_interval > 1440 else old_interval / 1440
            new_interval_days = old_interval_days * ((old_ease_factor + 30) / 100)
            new_interval_minutes = int(new_interval_days * 1440)

    else:
        # Invalid grade, return unchanged
        return (old_ease_factor, old_interval, old_repetition, is_learning)

    # Ensure minimum interval of 1 minute
    new_interval_minutes = max(1, new_interval_minutes)

    return (new_ease_factor, new_interval_minutes, new_repetition, new_is_learning)