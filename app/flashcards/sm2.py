"""
Anki Algorithm Implementation - Exact replica
"""


def anki_algorithm(
        grade,
        old_ease_factor,
        old_interval,
        old_repetition,
        is_learning=None
        ):
    """
    Apply exact Anki algorithm.
    grade: int (1=Again, 2=Good, 3=Easy)
    old_ease_factor: int (in percentage, e.g., 250 for 2.5x)
    old_interval: int (in minutes)
    old_repetition: int
    is_learning: bool (if None, auto-detect based on repetition)
    Returns: (new_ease_factor, new_interval_minutes, new_repetition,
              is_learning_phase)
    """
    MIN_EF = 130  # 1.3x in percentage form

    # Convert ease factor to percentage if it's in decimal form
    if old_ease_factor < 10:
        old_ease_factor = int(old_ease_factor * 100)

    # Auto-detect learning phase
    if is_learning is None:
        is_learning = old_repetition == 0

    new_ease_factor = old_ease_factor

    if grade == 1:  # Again
        # Reset to beginning of learning
        new_repetition = 0
        new_is_learning = True
        new_interval_minutes = 1  # 1 minute (immediate)
        # Reduce ease factor by 20% (like Anki)
        new_ease_factor = max(old_ease_factor - 20, MIN_EF)

    elif grade == 2:  # Good
        if is_learning or old_repetition == 0:
            # Learning phase
            if old_repetition == 0:
                # First time seeing card
                new_repetition = 1
                new_interval_minutes = 10  # 10 minutes
                new_is_learning = True
            elif old_repetition == 1:
                # Second time - graduate to review phase
                new_repetition = 2
                new_interval_minutes = 1440  # 1 day
                new_is_learning = False
            else:
                # Shouldn't happen in normal flow
                new_repetition = old_repetition + 1
                new_interval_minutes = 1440
                new_is_learning = False
        else:
            # Review phase - use ease factor
            new_repetition = old_repetition + 1
            new_is_learning = False

            # Convert to days for calculation
            old_interval_days = max(1, old_interval // 1440)
            new_interval_days = max(
                1,
                int(old_interval_days * (old_ease_factor / 100))
            )
            new_interval_minutes = new_interval_days * 1440

    elif grade == 3:  # Easy
        if is_learning or old_repetition <= 1:
            # Graduate immediately from learning
            new_repetition = 2
            new_is_learning = False
            new_interval_minutes = 4 * 1440  # 4 days (Anki's easy interval)
        else:
            # Review phase - easier than good
            new_repetition = old_repetition + 1
            new_is_learning = False

            # Convert to days for calculation
            old_interval_days = max(1, old_interval // 1440)
            # Easy multiplier = ease factor * 1.3 (Anki's easy bonus)
            easy_multiplier = (old_ease_factor / 100) * 1.3
            new_interval_days = max(
                1,
                int(old_interval_days * easy_multiplier)
            )
            new_interval_minutes = new_interval_days * 1440

        # Increase ease factor by 15% for easy (like Anki)
        new_ease_factor = old_ease_factor + 15

    else:
        # Invalid grade
        return (old_ease_factor, old_interval, old_repetition, is_learning)

    # Ensure minimum interval of 1 minute
    new_interval_minutes = max(1, new_interval_minutes)

    # Cap maximum interval at 36500 days (100 years) like Anki
    max_interval_minutes = 36500 * 1440
    new_interval_minutes = min(new_interval_minutes, max_interval_minutes)

    return (
        new_ease_factor,
        new_interval_minutes,
        new_repetition,
        new_is_learning
    )
