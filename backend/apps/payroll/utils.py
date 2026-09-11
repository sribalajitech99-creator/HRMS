from decimal import ROUND_HALF_UP, Decimal

from .services import money

_INR_WORDS = [
    "",
    "One",
    "Two",
    "Three",
    "Four",
    "Five",
    "Six",
    "Seven",
    "Eight",
    "Nine",
    "Ten",
    "Eleven",
    "Twelve",
    "Thirteen",
    "Fourteen",
    "Fifteen",
    "Sixteen",
    "Seventeen",
    "Eighteen",
    "Nineteen",
]

_TENS_WORDS = [
    "",
    "",
    "Twenty",
    "Thirty",
    "Forty",
    "Fifty",
    "Sixty",
    "Seventy",
    "Eighty",
    "Ninety",
]


def _two_digit_words(number):
    """Convert an integer in the range 0-99 to English words."""
    number = int(number)

    if number < 20:
        return _INR_WORDS[number]

    tens = number // 10
    units = number % 10

    word = _TENS_WORDS[tens]

    if units:
        word += " " + _INR_WORDS[units]

    return word


def _three_digit_words(number):
    """Convert an integer in the range 0-999 to English words."""
    number = int(number)

    hundreds = number // 100
    remainder = number % 100

    parts = []

    if hundreds:
        parts.append(_INR_WORDS[hundreds])
        parts.append("Hundred")

    if remainder:
        parts.append(_two_digit_words(remainder))

    return " ".join(parts).strip()


def number_in_words(number):
    """Convert a non-negative integer to Indian-system English words.

    Follows the Indian numbering system (lakhs and crores), e.g. 123456 -> 
    "One Lakh Twenty Three Thousand Four Hundred Fifty Six".
    """
    number = int(number)

    if number == 0:
        return "Zero"

    crore = number // 10000000
    number %= 10000000

    lakh = number // 100000
    number %= 100000

    thousand = number // 1000
    number %= 1000

    parts = []

    if crore:
        parts.append(_two_digit_words(crore))
        parts.append("Crore")

    if lakh:
        parts.append(_two_digit_words(lakh))
        parts.append("Lakh")

    if thousand:
        parts.append(_two_digit_words(thousand))
        parts.append("Thousand")

    if number:
        parts.append(_three_digit_words(number))

    return " ".join(parts)


def amount_in_words(value):
    """Return the Indian number-in-words representation of a money value.

    Example: 26200 -> "Rupees Twenty Six Thousand Two Hundred Only".
    Paise are appended when a fractional part is present.
    """
    value = money(value)

    rupee_part = int(value)

    paise_part = int(
        (
            (value - Decimal(rupee_part))
            * Decimal(100)
        ).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )

    parts = ["Rupees", number_in_words(rupee_part)]

    if paise_part:
        parts.append("and")
        parts.append(number_in_words(paise_part))
        parts.append("Paise")

    parts.append("Only")

    return " ".join(parts)


def indian_grouping(value):
    """Format a number with Indian-style digit grouping.

    Example: 2865123.50 -> "28,65,123.50"
    """
    value = money(value)

    text = f"{value:.2f}"

    integer_part, _, fraction = text.partition(".")

    sign = ""

    if integer_part.startswith("-"):
        sign = "-"
        integer_part = integer_part[1:]

    if len(integer_part) <= 3:
        grouped = integer_part
    else:
        last_three = integer_part[-3:]

        head = integer_part[:-3]

        head = "{:,}".format(int(head)).replace(",", ",")

        grouped = f"{head},{last_three}"

    return f"{sign}{grouped}.{fraction}"