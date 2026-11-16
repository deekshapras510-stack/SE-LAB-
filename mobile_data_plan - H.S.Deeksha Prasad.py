import math


def _parse_number(text):
    """Parse a plain non-negative decimal like '5' or '2.5'.

    Returns a finite float, or None if the text is not valid.
    """
    text = text.strip()
    if not text or not text.isascii() or '_' in text:
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    if not math.isfinite(value) or value < 0:  # rejects nan, inf, negatives
        return None
    return value


def parse_plan(text):
    """Parse 'standard:5' into ('Standard', 5.0).

    Returns None if the input is invalid.
    """
    if not isinstance(text, str):
        return None
    parts = text.split(':')
    if len(parts) != 2:
        return None
    plan = parts[0].strip()
    gb = _parse_number(parts[1])
    if not plan or gb is None:
        return None
    return plan.title(), gb


def usage_average(usage_csv):
    """Return the integer average of a CSV of daily MB usage, e.g. '300,450,800'.

    Returns None if the input is invalid.
    """
    if not isinstance(usage_csv, str):
        return None
    values = []
    for r in usage_csv.split(','):
        r = r.strip()
        # ASCII digits only: rejects '', '-5', '1.5', '1_0', '²', 'abc'
        if not (r and r.isascii() and r.isdigit()):
            return None
        try:
            values.append(int(r))
        except ValueError:  # absurdly long digit strings
            return None
    if not values:
        return None
    return sum(values) // len(values)


def payable_bill(text):
    """Parse 'bill|discount' (e.g. '399|50'), add 18% GST, subtract discount.

    Result is never negative. Returns None if the input is invalid.
    """
    if not isinstance(text, str):
        return None
    parts = text.split('|')
    if len(parts) != 2:
        return None
    bill = _parse_number(parts[0])
    discount = _parse_number(parts[1])
    if bill is None or discount is None:
        return None
    total = bill * 1.18 - discount
    if not math.isfinite(total):  # e.g. overflow on huge values
        return None
    return round(max(total, 0), 2)


def main():
    print("==== Running parse_plan ====")
    user_input = input("Enter plan:data in GB (e.g. standard:5): ")
    result = parse_plan(user_input)
    print("Plan and Data:", result if result is not None else "Invalid plan")

    print("\n==== Running usage_average ====")
    user_input = input("Enter daily usage in MB as CSV (e.g. 300,450,800): ")
    result = usage_average(user_input)
    print("Average Usage:", result if result is not None else "Invalid usage data")

    print("\n==== Running payable_bill ====")
    user_input = input("Enter bill|discount (e.g. 399|50): ")
    result = payable_bill(user_input)
    print("Payable Bill:", result if result is not None else "Invalid bill")


if __name__ == "__main__":
    main()
