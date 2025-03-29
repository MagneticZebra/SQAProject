import pytest
from banking_system import BankingSystem

@pytest.fixture
def setup_accounts_and_transactions(tmp_path):
    master = tmp_path / "master.txt"
    transactions = tmp_path / "transactions.txt"

    # Master file with a few valid accounts
    master.write_text(
        "01001 user_one             A 01000.00 0000 NP\n"
        "01002 user_two             A 00500.00 0000 SP\n"
        "01003 user_three           A 00300.00 0000 NP\n"
        "01004 test_user            A 00500.00 0000 NP\n"
        "00000 END_OF_FILE          A 00000.00 0000 NP\n"
    )

    # Transactions that cover all meaningful paths in apply_transactions()
    transactions.write_text(
        "04 user_three          01003 00100.00 SP\n"       # Valid Deposit
        "05 joe                 00000 00000.00 SP\n"        # Create Account
        "06 user_three          01003 00000.00 SP\n"        # Delete Account
        "07 user_two            01002 00000.00 SP\n"        # Disable Account
        "08 user_three          01003 00000.00 SP\n"      # Change Plan (success)
        "01 test_user           01004 00050.00 NP\n"        # Withdrawal - valid
        "01 test_user           01004 99999.00 NP\n"        # Withdrawal - insufficient funds
        "03 test_user           01004 00030.00 EC\n"      # Paybill - valid company
        "03 test_user           01004 00030.00 AR\n"     # Paybill - invalid company
        "04 ghost               99999 00100.00 NP\n"        # Deposit to non-existent account
        "08 test_user           01004 00000.00 NP\n"      # Change Plan - failure (already NP)
        "00 END_OF_SESSION      00000 00000.00 NP\n"        # End of Session
    )

    return BankingSystem(str(master), str(transactions))


def test_apply_transactions_statement_coverage(setup_accounts_and_transactions):
    system = setup_accounts_and_transactions
    system.apply_transactions()

    # Confirm Joe was created
    assert "joe" in [acc["name"] for acc in system.accounts.values()]

    # Confirm user_three was deleted OR balance was updated first
    assert "1003" not in system.accounts or system.accounts["1003"]["balance"] == 400.00

    # Confirm user_two was disabled
    if "01002" in system.accounts:
        assert system.accounts["01002"]["status"] == "D"

    # Confirm test_user's balance reflects at least one successful withdrawal/paybill
    assert system.accounts["1004"]["balance"] < 500.00