import pytest
from hypothesis import given, strategies as st
from mobile_data_plan import parse_plan, usage_average, payable_bill


# ---------- 1. No-crash fuzz tests ----------

@given(st.text() | st.none())
def test_parse_plan_no_crash(s):
    try:
        parse_plan(s)
    except Exception as e:
        assert False, f"parse_plan crashed with: {e!r} on input {s!r}"


@given(st.text() | st.none())
def test_usage_average_no_crash(s):
    try:
        usage_average(s)
    except Exception as e:
        assert False, f"usage_average crashed with: {e!r} on input {s!r}"


@given(st.text() | st.none())
def test_payable_bill_no_crash(s):
    try:
        payable_bill(s)
    except Exception as e:
        assert False, f"payable_bill crashed with: {e!r} on input {s!r}"


# ---------- 2. Extra: non-string types must not crash ----------

@given(st.one_of(st.integers(), st.floats(), st.lists(st.integers()),
                 st.booleans(), st.none()))
def test_all_functions_handle_non_strings(x):
    for fn in (parse_plan, usage_average, payable_bill):
        try:
            fn(x)
        except Exception as e:
            assert False, f"{fn.__name__} crashed with: {e!r} on input {x!r}"


# ---------- 3. Extra: correctness on valid inputs ----------

@given(st.from_regex(r"[A-Za-z]{1,10}", fullmatch=True),
       st.floats(min_value=0, max_value=1000,
                 allow_nan=False, allow_infinity=False))
def test_parse_plan_valid(plan, gb):
    assert parse_plan(f"{plan}:{gb!r}") == (plan.title(), gb)


@given(st.lists(st.integers(min_value=0, max_value=10**6),
                min_size=1, max_size=20))
def test_usage_average_valid(values):
    csv = ",".join(str(v) for v in values)
    assert usage_average(csv) == sum(values) // len(values)


@given(st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False))
def test_payable_bill_valid(bill, discount):
    result = payable_bill(f"{bill!r}|{discount!r}")
    assert result >= 0
    assert result == pytest.approx(max(bill * 1.18 - discount, 0), abs=0.01)
