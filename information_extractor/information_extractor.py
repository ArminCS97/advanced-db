import hashlib


def get_trailing_zeros(hash_value):
    """Return the number of trailing 0s in binary representation of hash_value."""
    binary_representation = bin(hash_value)[2:]  # Convert to binary and remove the '0b' prefix
    trailing_zeros_count = 0
    for digit in reversed(binary_representation):
        if digit == '0':
            trailing_zeros_count += 1
        else:
            break  # Stop counting when the first '1' is encountered from the end
    return trailing_zeros_count


def count_number_of_distinct_words(stream_words):
    r = 0  # a variable to record the number of different values
    for word in stream_words:
        hash_value = int(hashlib.sha256(word.encode('utf-8')).hexdigest(), 16)
        r = max(r, get_trailing_zeros(hash_value))
    return 2 ** r
