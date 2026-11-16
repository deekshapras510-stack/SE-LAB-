"""
Lab 6 - Branch Coverage tests for mobile_data_plan.py

Goal: make every decision evaluate to BOTH True and False, including
boundary values (<=, >, >=) and combined conditions (and / or).
Run:
    coverage run --branch -m pytest BranchCoverageTest_mobile_data_plan.py
    coverage report -m
"""
import pytest
from mobile_data_plan import overage_charge, recharge_allowed, validity_status


# ---------------------------------------------------------------
# Starter examples
# ---------------------------------------------------------------
def test_within_included_data():
    assert overage_charge("standard", 3, False, False) == 0


def test_recharge_allowed():
    assert recharge_allowed(500, 1, False) is True


# ===============================================================
# overage_charge
# ===============================================================

# --- if plan not in INCLUDED_GB  (True / False) ---
def test_overage_unknown_plan_raises():
    with pytest.raises(ValueError, match="unknown plan"):
        overage_charge("gold", 1, False, False)


@pytest.mark.parametrize("plan", ["basic", "standard", "premium"])
def test_overage_known_plans_accepted(plan):
    # False side of the "unknown plan" check
    assert overage_charge(plan, 0, False, False) == 0


# --- if data_gb < 0  (True / False, boundary at 0) ---
def test_overage_negative_usage_raises():
    with pytest.raises(ValueError, match="invalid data usage"):
        overage_charge("basic", -1, False, False)


def test_overage_zero_usage_is_valid():
    assert overage_charge("basic", 0, False, False) == 0


# --- if is_loyal and plan != "premium" ---
def test_overage_loyal_basic_gets_bonus_gb():
    # loyal=True, plan!=premium -> True ; included becomes 3
    assert overage_charge("basic", 3, False, True) == 0


def test_overage_loyal_basic_bonus_is_exactly_one_gb():
    # 4 GB used, 3 included -> 1 extra * 15
    assert overage_charge("basic", 4, False, True) == 15


def test_overage_loyal_standard_gets_bonus_gb():
    # included becomes 6, so 6 GB is free and 7 GB costs 1 * 15
    assert overage_charge("standard", 6, False, True) == 0
    assert overage_charge("standard", 7, False, True) == 15


def test_overage_loyal_premium_gets_no_bonus():
    # loyal=True but plan == premium -> False ; included stays 10
    assert overage_charge("premium", 11, False, True) == 15


def test_overage_not_loyal_gets_no_bonus():
    # loyal=False -> False (short-circuits the 'and')
    assert overage_charge("basic", 3, False, False) == 15


# --- if extra <= 0  (True / False, boundary at 0) ---
def test_overage_exactly_at_limit_is_free():
    assert overage_charge("basic", 2, False, False) == 0


def test_overage_just_above_limit_is_charged():
    assert overage_charge("basic", 3, False, False) == 15


def test_overage_below_limit_is_free():
    assert overage_charge("premium", 1, True, False) == 0


# --- if is_roaming  (True / False) for the base rate ---
def test_overage_domestic_rate():
    assert overage_charge("basic", 5, False, False) == 3 * 15


def test_overage_roaming_rate():
    assert overage_charge("basic", 5, True, False) == 3 * 40


# --- if extra > 10  (True / False, boundary at 10) ---
def test_overage_extra_exactly_ten_uses_normal_rate():
    # extra == 10 -> NOT > 10
    assert overage_charge("basic", 12, False, False) == 10 * 15
    assert overage_charge("basic", 12, True, False) == 10 * 40


def test_overage_extra_eleven_uses_surcharge_rate_domestic():
    # extra == 11 -> rate 15 + 10 = 25 ; inner is_roaming False
    assert overage_charge("basic", 13, False, False) == 11 * 25


def test_overage_extra_eleven_uses_surcharge_rate_roaming():
    # extra == 11 -> rate 40 + 10 + 5 = 55 ; inner is_roaming True
    assert overage_charge("basic", 13, True, False) == 11 * 55


def test_overage_large_usage_premium_roaming():
    assert overage_charge("premium", 30, True, False) == 20 * 55


def test_overage_fractional_usage():
    assert overage_charge("basic", 2.5, False, False) == pytest.approx(0.5 * 15)


# ===============================================================
# recharge_allowed
# ===============================================================

# --- if is_kyc_pending  (True / False) ---
def test_recharge_kyc_pending_small_amount_allowed():
    assert recharge_allowed(150, 0, True) is True


def test_recharge_kyc_pending_boundary_200_allowed():
    assert recharge_allowed(200, 0, True) is True


def test_recharge_kyc_pending_above_200_rejected():
    assert recharge_allowed(201, 0, True) is False


def test_recharge_kyc_pending_ignores_pending_recharges():
    # KYC branch returns before pending_recharges is ever checked
    assert recharge_allowed(100, 99, True) is True


# --- if amount > 2000  (True / False, boundary at 2000) ---
def test_recharge_amount_over_2000_rejected():
    assert recharge_allowed(2001, 0, False) is False


def test_recharge_amount_exactly_2000_allowed():
    assert recharge_allowed(2000, 0, False) is True


# --- return pending_recharges <= 2  (True / False, boundary at 2) ---
def test_recharge_pending_exactly_two_allowed():
    assert recharge_allowed(500, 2, False) is True


def test_recharge_pending_three_rejected():
    assert recharge_allowed(500, 3, False) is False


def test_recharge_no_pending_allowed():
    assert recharge_allowed(500, 0, False) is True


# ===============================================================
# validity_status
# ===============================================================

# --- if is_prepaid  (True -> cutoff 0 / False -> cutoff 3) ---
# --- if has_addon   (True -> cutoff + 2 / False -> unchanged) ---

# cutoff = 0  (prepaid, no add-on)
def test_validity_prepaid_no_addon_active_at_cutoff():
    assert validity_status(0, True, False) == "active"


def test_validity_prepaid_no_addon_grace_just_below_cutoff():
    assert validity_status(-1, True, False) == "grace"


def test_validity_prepaid_no_addon_grace_lower_boundary():
    # cutoff - 15 = -15 -> still grace
    assert validity_status(-15, True, False) == "grace"


def test_validity_prepaid_no_addon_expired():
    assert validity_status(-16, True, False) == "expired"


# cutoff = 3  (postpaid, no add-on)
def test_validity_postpaid_no_addon_active_at_cutoff():
    assert validity_status(3, False, False) == "active"


def test_validity_postpaid_no_addon_grace_just_below_cutoff():
    assert validity_status(2, False, False) == "grace"


def test_validity_postpaid_no_addon_grace_lower_boundary():
    # cutoff - 15 = -12
    assert validity_status(-12, False, False) == "grace"


def test_validity_postpaid_no_addon_expired():
    assert validity_status(-13, False, False) == "expired"


# cutoff = 2  (prepaid + add-on)
def test_validity_prepaid_addon_active_at_cutoff():
    assert validity_status(2, True, True) == "active"


def test_validity_prepaid_addon_grace_just_below_cutoff():
    assert validity_status(1, True, True) == "grace"


def test_validity_prepaid_addon_grace_lower_boundary():
    # cutoff - 15 = -13
    assert validity_status(-13, True, True) == "grace"


def test_validity_prepaid_addon_expired():
    assert validity_status(-14, True, True) == "expired"


# cutoff = 5  (postpaid + add-on)
def test_validity_postpaid_addon_active_at_cutoff():
    assert validity_status(5, False, True) == "active"


def test_validity_postpaid_addon_grace_just_below_cutoff():
    assert validity_status(4, False, True) == "grace"


def test_validity_postpaid_addon_grace_lower_boundary():
    # cutoff - 15 = -10
    assert validity_status(-10, False, True) == "grace"


def test_validity_postpaid_addon_expired():
    assert validity_status(-11, False, True) == "expired"
