import pytest
from banking_system import BankingSystem

# -----------------------------
# System & patch accounts
# -----------------------------
@pytest.fixture
def system(tmp_path):
    # Dummy files — won't be used but required by init
    master = tmp_path / "master.txt"
    transactions = tmp_path / "transactions.txt"
    master.write_text("00000 END_OF_FILE          A 00000.00 0000 NP\n")
    transactions.write_text("00 END_OF_SESSION       00000 00000.00 NP\n")

    bs = BankingSystem(str(master), str(transactions))
    return bs

#region Decision Coverage Tests
# -----------------------------
# DECISION COVERAGE TESTS
# -----------------------------

def test_skip_eof_account(system):
    system.accounts = {
        "00000": {"account_number": "00000", "balance": 0.0, "total_transactions": 3, "plan": "SP"}
    }
    system.calculate_transaction_fee()
    assert system.accounts["00000"]["balance"] == 0.0  # Balance unchanged


def test_apply_sp_fee(system):
    system.accounts = {
        "1001": {"account_number": "1001", "balance": 100.0, "total_transactions": 2, "plan": "SP"}
    }
    system.calculate_transaction_fee()
    assert system.accounts["1001"]["balance"] == 99.90  # 100 - 2(0.05)


def test_apply_np_fee(system):
    system.accounts = {
        "1002": {"account_number": "1002", "balance": 100.0, "total_transactions": 2, "plan": "NP"}
    }
    system.calculate_transaction_fee()
    assert system.accounts["1002"]["balance"] == 99.80  # 100 - 2(0.10)


def test_sufficient_funds(system):
    system.accounts = {
        "1002": {"account_number": "1002", "balance": 5.00, "total_transactions": 2, "plan": "NP"}
    }
    system.calculate_transaction_fee()
    assert system.accounts["1002"]["balance"] == 4.80 # 5.00 - 2(0.10)


def test_insufficient_funds(system):
    system.accounts = {
        "1001": {"account_number": "1001", "balance": 0.01, "total_transactions": 2, "plan": "SP"}
    }
    system.calculate_transaction_fee()
    assert system.accounts["1001"]["balance"] <= 0.0


def test_zero_transactions(system):
    system.accounts = {
        "1001": {"account_number": "1001", "balance": 100.0, "total_transactions": 0, "plan": "SP"}
    }
    system.calculate_transaction_fee()
    assert system.accounts["1001"]["balance"] == 100.0


def test_sp_fee_edge(system):
    system.accounts = {
        "1001": {"account_number": "1001", "balance": 0.10, "total_transactions": 2, "plan": "SP"}
    }
    system.calculate_transaction_fee()
    assert system.accounts["1001"]["balance"] == 0.0


def test_np_fee_edge(system):
    system.accounts = {
        "1002": {"account_number": "1002", "balance": 0.30, "total_transactions": 3, "plan": "NP"}
    }
    system.calculate_transaction_fee()
    assert system.accounts["1002"]["balance"] == 0.0


def test_invalid_plan_type(system):
    system.accounts = {
        "1003": {"account_number": "1003", "balance": 100.0, "total_transactions": 2, "plan": "XX"}
    }
    # Invalid plan still uses 0.10 so it charges fee
    #assert system.accounts["1003"]["balance"] == 99.80
    with pytest.raises(SystemExit):
        system.calculate_transaction_fee()


def test_negative_transaction_count(system):
    system.accounts = {
        "1003": {"account_number": "1003", "balance": 100.0, "total_transactions": -1, "plan": "SP"}
    }
    system.calculate_transaction_fee()
    assert system.accounts["1003"]["balance"] == 100.0  # Fee not applied


def test_fee_rounding_edge(system):
    system.accounts = {
        "1001": {"account_number": "1001", "balance": 0.11, "total_transactions": 2, "plan": "SP"}
    }
    system.calculate_transaction_fee()
    assert system.accounts["1001"]["balance"] <= 0.1  # Due to rounding logic


def test_exact_balance_for_fee(system):
    system.accounts = {
        "1001": {"account_number": "1001", "balance": 0.10, "total_transactions": 2, "plan": "SP"}
    }
    system.calculate_transaction_fee()
    assert system.accounts["1001"]["balance"] == 0.0


def test_very_high_transaction_count(system):
    system.accounts = {
        "1002": {"account_number": "1002", "balance": 100.0, "total_transactions": 1000, "plan": "NP"}
    }
    system.calculate_transaction_fee()
    assert system.accounts["1002"]["balance"] == 0.0  # 1000 * 0.10 = $100

def test_minimum_balance_np(system):
    system.accounts = {
        "1002": {"account_number": "1002", "balance": 0.10, "total_transactions": 1, "plan": "NP"}
    }
    system.calculate_transaction_fee()
    assert system.accounts["1002"]["balance"] == 0.0

#endregion

#region Loop Coverage Tests
# -----------------------------
# LOOP COVERAGE TESTS
# -----------------------------
# -----------------------------
# LOOP COVERAGE TESTS
# -----------------------------

def test_loop_zero_accounts(system):
    # No accounts → loop body should not run
    system.accounts = {}
    system.calculate_transaction_fee()
    assert system.accounts == {}  # Nothing changed

def test_loop_one_account(system):
    # One SP account → loop should run once
    system.accounts = {
        "1001": {
            "account_number": "1001",
            "balance": 10.00,
            "total_transactions": 2,
            "plan": "SP"
        }
    }
    system.calculate_transaction_fee()
    assert system.accounts["1001"]["balance"] == 9.90  # 10.00 - 2(0.05)


def test_loop_multiple_accounts(system):
    # Two accounts, loop should run twice
    system.accounts = {
        "1001": {
            "account_number": "1001",
            "balance": 20.00,
            "total_transactions": 2,
            "plan": "SP"
        },
        "1002": {
            "account_number": "1002",
            "balance": 30.00,
            "total_transactions": 3,
            "plan": "NP"
        }
    }
    system.calculate_transaction_fee()
    assert system.accounts["1001"]["balance"] == 19.90  # 20.00 - 2(0.05)
    assert system.accounts["1002"]["balance"] == 29.70  # 30.00 - 3(0.10)

#endregion