"""
Lab 6 - Code (Line) Coverage tests for mobile_data_plan.py

Goal: execute every line of the application at least once.
Run:
    coverage run -m pytest CodeCoverageTest_mobile_data_plan.py
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


# ---------------------------------------------------------------
# overage_charge
# ---------------------------------------------------------------
def test_overage_unknown_plan_raises():
    with pytest.raises(ValueError, match="unknown plan"):
        overage_charge("gold", 1, False, False)


def test_overage_negative_usage_raises():
    with pytest.raises(ValueError, match="invalid data usage"):
        overage_charge("basic", -1, False, False)


def test_overage_loyal_basic_gets_bonus_gb():
    # basic = 2 GB, loyal adds 1 -> 3 GB included, so 3 GB used is free
    assert overage_charge("basic", 3, False, True) == 0


def test_overage_domestic_normal_rate():
    # basic, 2 GB included, 5 GB used -> 3 extra * Rs.15
    assert overage_charge("basic", 5, False, False) == 45


def test_overage_roaming_normal_rate():
    # basic, 2 GB included, 5 GB used -> 3 extra * Rs.40
    assert overage_charge("basic", 5, True, False) == 120


def test_overage_domestic_heavy_usage_rate():
    # basic, 2 GB included, 15 GB used -> 13 extra * (15 + 10)
    assert overage_charge("basic", 15, False, False) == 13 * 25


def test_overage_roaming_heavy_usage_rate():
    # basic, 2 GB included, 15 GB used -> 13 extra * (40 + 10 + 5)
    assert overage_charge("basic", 15, True, False) == 13 * 55


# ---------------------------------------------------------------
# recharge_allowed
# ---------------------------------------------------------------
def test_recharge_kyc_pending_small_amount_allowed():
    assert recharge_allowed(150, 0, True) is True


def test_recharge_over_limit_rejected():
    assert recharge_allowed(2500, 0, False) is False


def test_recharge_too_many_pending_rejected():
    assert recharge_allowed(500, 3, False) is False


# ---------------------------------------------------------------
# validity_status
# ---------------------------------------------------------------
def test_validity_prepaid_active():
    assert validity_status(5, True, False) == "active"


def test_validity_postpaid_with_addon_grace():
    # cutoff = 3 + 2 = 5 ; 2 days left is below 5 but >= 5 - 15
    assert validity_status(2, False, True) == "grace"


def test_validity_prepaid_expired():
    # cutoff = 0 ; -20 days is below the grace window (-15)
    assert validity_status(-20, True, False) == "expired"
