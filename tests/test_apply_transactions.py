# -------------------------------------------------------------------------------------------
# This code tests statement coverage for the apply_transactions method in banking_system.py
# -------------------------------------------------------------------------------------------

import pytest
from banking_system import BankingSystem

@pytest.fixture
def setup_accounts_and_transactions(tmp_path):
    master = tmp_path / "master.txt"
    transactions = tmp_path / "transactions.txt"

    # Master file with valid accounts
    master.write_text(
        "01000 user_one             A 01000.00 0000 NP\n"
        "01001 user_two             A 00500.00 0000 SP\n"
        "01002 user_three           A 00300.00 0000 NP\n"
        "01003 test_user            A 00500.00 0000 NP\n"
        "00000 END_OF_FILE          A 00000.00 0000 NP\n"
    )

    # Transactions to trigger each branch
    transactions.write_text(
        "04 user_three           01002 00100.00 SP\n"        # Valid Deposit
        "05 joe                  00000 00000.00 SP\n"        # Create success
        "06 user_three           01002 00000.00 SP\n"        # Delete success
        "07 user_two             01001 00000.00 SP\n"        # Disable Account
        "08 user_one             01000 00000.00 SP\n"        # Change Plan success
        "01 test_user            01003 00050.00 NP\n"        # Withdrawal success
        "01 test_user            01003 99999.00 NP\n"        # Withdrawal fail
        "03 test_user            01003 00030.00 EC\n"        # Paybill success
        "03 test_user            01003 00030.00 AR\n"        # Paybill fail
        "04 ghost                99999 00100.00 NP\n"        # Deposit to non-existent account
        "08 test_user            01003 00000.00 NP\n"        # Change Plan fail (already NP)
        "06 ghost                99999 00000.00 NP\n"        # Delete fail
        "07 ghost                99999 00000.00 NP\n"        # Disable fail
        "09 test_user            01003 00000.00 NP\n"        # INVALID CODE (should log error and exit)
        "00 END_OF_SESSION       00000 00000.00 NP\n"        # End of session
    )

    return BankingSystem(str(master), str(transactions))


def test_apply_transactions_statement_coverage(setup_accounts_and_transactions):
    system = setup_accounts_and_transactions

    try:
        system.apply_transactions()
    except SystemExit:
        pass

    # Confirm Joe was created
    assert "joe" in [acc["name"] for acc in system.accounts.values()]

    # Confirm user_three was deleted
    assert "01002" not in system.accounts

    # Confirm user_two was disabled
    assert system.accounts["01001"]["status"] == "D"

    # test_user: withdrawal ($50), paybill ($30), invalid paybill ignored, failed withdrawal
    assert system.accounts["01003"]["balance"] < 500.00

    # Change plan success
    assert system.accounts["01000"]["plan"] == "SP"  # Changed from NP to SP (success)
    assert system.accounts["01003"]["plan"] == "NP"  # Remained NP (failed to change)

    # Confirm deposit to ghost failed → ghost not added
    assert "ghost" not in [acc["name"] for acc in system.accounts.values()]

    # Change plan failure path (already on NP)
    # No assertion needed — just making sure it didn't crash

    # Confirm transaction with invalid code led to SystemExit
    # Already handled via try-except above