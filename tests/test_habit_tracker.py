# tests/test_habit_tracker.py

import pytest
import os
import shutil
from datetime import datetime, timedelta
from main import app, habit_tracker, config_manager  # Import from your main code
from typer.testing import CliRunner

runner = CliRunner()

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """
    A fixture that runs before and after each test.
    Cleans up or sets up as needed.
    """
    # Before each test: ensure we start fresh
    if os.path.exists(habit_tracker.DATA_FILE):
        os.remove(habit_tracker.DATA_FILE)
    if os.path.exists(habit_tracker.USER_FILE):
        os.remove(habit_tracker.USER_FILE)
    if os.path.exists(config_manager.CONFIG_FILE):
        os.remove(config_manager.CONFIG_FILE)
    yield
    # After each test: also remove any leftover files
    if os.path.exists(habit_tracker.DATA_FILE):
        os.remove(habit_tracker.DATA_FILE)
    if os.path.exists(habit_tracker.USER_FILE):
        os.remove(habit_tracker.USER_FILE)
    if os.path.exists(config_manager.CONFIG_FILE):
        os.remove(config_manager.CONFIG_FILE)

def test_setup_user():
    """
    Test setting up a user using the CLI command `setup-user`.
    """
    result = runner.invoke(app, ["setup-user"], input="TestUser\n")
    assert result.exit_code == 0
    assert "Username 'TestUser' has been set successfully!" in result.output

def test_add_habit():
    # Start with a clean environment
    runner.invoke(app, ["reset"])
    
    # Must set up user first
    runner.invoke(app, ["setup-user"], input="Tester\n")
    # Now add
    result = runner.invoke(app, ["add", "Workout", "daily"])
    assert result.exit_code == 0
    assert "Habit 'Workout' (daily) added successfully!" in result.output


def test_check_habit_without_date():
    """
    Test checking off a habit (default today's date).
    """
    runner.invoke(app, ["setup-user"], input="Tester\n")
    runner.invoke(app, ["add", "Workout", "daily"])
    result = runner.invoke(app, ["check", "Workout"])
    assert result.exit_code == 0
    # Now we look for "Checked off 'Workout' (daily) on " in result.output
    assert "Checked off 'Workout' (daily) on " in result.output


def test_check_habit_with_date():
    """
    Test checking off a habit with a custom date.
    """
    runner.invoke(app, ["setup-user"], input="Tester\n")
    runner.invoke(app, ["add", "ReadBook", "daily"])
    # Provide a date in YYYY-MM-DD
    custom_date = "2023-05-01"
    result = runner.invoke(app, ["check", "ReadBook", "--date", custom_date])
    assert result.exit_code == 0
    assert f"Checked off 'ReadBook' (daily) on 2023-05-01T" in result.output  # partial match

def test_delete_habit_without_date():
    """
    Test deleting an entire habit (no --date).
    """
    runner.invoke(app, ["setup-user"], input="Tester\n")
    runner.invoke(app, ["add", "GuitarPractice", "daily"])
    result = runner.invoke(app, ["delete", "GuitarPractice"])
    assert result.exit_code == 0
    assert "deleted entirely" in result.output

def test_delete_habit_with_date():
    """
    Test removing a single check from logs for a specific date.
    """
    runner.invoke(app, ["setup-user"], input="Tester\n")
    runner.invoke(app, ["add", "PayBills", "weekly"])
    # Check it for 2023-05-10
    runner.invoke(app, ["check", "PayBills", "--date", "2023-05-10"])
    # Now remove that single check
    result = runner.invoke(app, ["delete", "PayBills", "--date", "2023-05-10"])
    assert result.exit_code == 0
    assert "Removed 1 checks dated 2023-05-10" in result.output

def test_fill_data():
    """
    Test the `fill` command to generate sample data.
    """
    runner.invoke(app, ["setup-user"], input="Tester\n")
    result = runner.invoke(app, ["fill"])
    assert result.exit_code == 0
    assert "Fake data added successfully" in result.output

def test_summary():
    """
    Test the `summary` command with some data.
    """
    runner.invoke(app, ["setup-user"], input="Tester\n")
    runner.invoke(app, ["add", "Workout", "daily"])
    runner.invoke(app, ["add", "PayBills", "weekly"])
    runner.invoke(app, ["check", "Workout"])
    result = runner.invoke(app, ["summary"])
    assert result.exit_code == 0
    # The output might contain lines about total habits, total check-ins, etc.
    # We can check for partial strings:
    assert "Total habits:" in result.output
    assert "Total check-ins:" in result.output
    assert "Pending Habits" in result.output or "No pending habits" in result.output
    assert "Habits you struggled with the most last month:" in result.output

def test_reminder():
    """
    Test the `reminder` command to see if it shows pending habits.
    """
    runner.invoke(app, ["setup-user"], input="Tester\n")
    runner.invoke(app, ["add", "Meditation", "daily"])
    # Not checking it off, so it should appear as pending
    result = runner.invoke(app, ["reminder"])
    assert result.exit_code == 0
    # It should mention "You have pending habits to complete" or show "Meditation"
    assert "Meditation (daily)" in result.output or "You have pending habits" in result.output
