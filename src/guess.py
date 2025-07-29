from collections import Counter
import random

def generate_random_guess():
    return sorted(random.sample(range(1, 50), 6))

def get_number_frequencies(df):
    all_numbers = [num for sublist in df["Winning Numbers"] for num in sublist]
    freq = Counter(all_numbers)
    return freq

# Weighted guess
def generate_smart_guess(df, strategy="frequent", exclude_recent=True, weight_strength=1.0):
    freq = get_number_frequencies(df)

    if exclude_recent:
        recent_numbers = set()
        for row in df.head(5)["Winning Numbers"]:
            recent_numbers.update(row)
    else:
        recent_numbers = set()

    # Create a weight for each number
    all_numbers = list(range(1, 50))
    frequencies = {n: freq.get(n, 0) for n in all_numbers}

    # Transform frequency into weights
    max_freq = max(frequencies.values())
    weights = {}

    for num in all_numbers:
        norm_freq = frequencies[num] / max_freq if max_freq > 0 else 0
        if strategy == "frequent":
            weights[num] = norm_freq ** weight_strength
        else:  # "rare"
            weights[num] = (1 - norm_freq) ** weight_strength

    # Remove recently drawn numbers if needed
    candidate_numbers = [n for n in all_numbers if n not in recent_numbers]
    candidate_weights = [weights[n] for n in candidate_numbers]

    # Normalize weights
    total_weight = sum(candidate_weights)
    probabilities = [w / total_weight for w in candidate_weights]

    guess = sorted(random.choices(candidate_numbers, weights=probabilities, k=6))
    return guess


def generate_clustered_guess(df, exclude_recent=True):
    freq = get_number_frequencies(df)

    # Get recently drawn numbers
    recent_numbers = set()
    if exclude_recent:
        for row in df.head(5)["Winning Numbers"]:
            recent_numbers.update(row)

    # Frequency-based clustering
    all_numbers = list(range(1, 50))
    freq_counts = {n: freq.get(n, 0) for n in all_numbers}
    sorted_numbers = sorted(freq_counts.items(), key=lambda x: x[1], reverse=True)

    n = len(sorted_numbers)
    hot = [num for num, _ in sorted_numbers[:n//3]]
    warm = [num for num, _ in sorted_numbers[n//3:2*n//3]]
    cold = [num for num, _ in sorted_numbers[2*n//3:]]

    if exclude_recent:
        hot = [n for n in hot if n not in recent_numbers]
        warm = [n for n in warm if n not in recent_numbers]
        cold = [n for n in cold if n not in recent_numbers]

    try:
        guess = (
            random.sample(hot, 2) +
            random.sample(warm, 2) +
            random.sample(cold, 2)
        )
        return sorted(guess)
    except ValueError:
        return generate_random_guess()