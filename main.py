import typer
import json
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
import matplotlib.pyplot as plt
import os
import random

####################################
# Helpers for graceful error handling
####################################
def handle_error(e: Exception, message: str = "An error occurred"):
    """
    Print a user-friendly error instead of a full traceback.
    Avoids system pop-up errors and Python stack traces.
    """
    typer.echo(f"[red]{message}[/red]")
    typer.echo(f"[yellow]Details: {str(e)}[/yellow]")

####################################
# Main HabitTracker class
####################################
class HabitTracker:
    DATA_FILE = "habits.json"
    USER_FILE = "user.json"

    def __init__(self):
        self.console = Console()
        self.data = self.load_data()
        self.username = self.load_user()

    def load_data(self):
        try:
            with open(self.DATA_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"habits": {}, "logs": {}}
        except Exception as e:
            self.console.print(f"[red]Error loading data: {e}[/red]")
            return {"habits": {}, "logs": {}}

    def save_data(self):
        try:
            with open(self.DATA_FILE, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            self.console.print(f"[red]Error saving data: {e}[/red]")

    def load_user(self):
        try:
            with open(self.USER_FILE, "r") as f:
                user_data = json.load(f)
                return user_data.get("username", "")
        except FileNotFoundError:
            return self.setup_user()
        except Exception as e:
            self.console.print(f"[red]Error loading user info: {e}[/red]")
            return ""

    def setup_user(self):
        try:
            username = self.console.input("[cyan]Enter your name to set up Habit Tracker: [/cyan]")
            with open(self.USER_FILE, "w") as f:
                json.dump({"username": username}, f, indent=4)
            return username
        except Exception as e:
            self.console.print(f"[red]Error setting up user: {e}[/red]")
            return ""

    def show_welcome_message(self):
        try:
            if self.username:
                self.console.print(
                    f"[green]Welcome back, {self.username}, to HCLI - Your Personal Habit Tracker![/green]"
                )
                self.console.print("[yellow]Stay consistent and track your progress effortlessly.[/yellow]")
                self.console.print("\n[yellow]Useful commands:")
                self.console.print("- `add <habit> <daily/weekly>`: Add a new habit")
                self.console.print("- `check <habit>`: Mark a habit as completed")
                self.console.print("- `list`: Show all habits")
                self.console.print("- `streaks`: View your habit streaks")
                self.console.print("- `summary`: View analytics and performance")
                self.console.print("- `reminder`: Get reminders for pending habits")
                self.console.print("- `dashboard`: Show a graphical analysis of habits")
                self.console.print("- `delete <habit>`: Remove a habit")
                self.console.print("- `details <habit>`: Show detailed info about a habit")
                self.console.print("- `fill`: Populate fake data for testing.")
                self.console.print("- `reset`: Reset all habits and logs.")

                # Show a summary of the current habit tracking status
                if hasattr(self, 'summary') and callable(getattr(self, 'summary', None)):
                    self.console.print("\n[blue]Habit Tracking Summary:[/blue]")
                    self.summary()
                else:
                    self.console.print("\n[blue]No habit tracking summary available yet.[/blue]")

                # Show pending habits
                if hasattr(self, 'reminder') and callable(getattr(self, 'reminder', None)):
                    self.console.print("\n[red]Pending Habit Reminders:[/red]")
                    self.reminder()
                else:
                    self.console.print("\n[green]No pending habit reminders.[/green]")
            else:
                self.console.print("[cyan]Welcome to Habit Tracker! Set up your profile to begin.[/cyan]")
        except Exception as e:
            self.console.print(f"[red]Error displaying welcome message: {e}[/red]")

    def add_habit(self, name: str, periodicity: str):
        try:
            if not name or not periodicity:
                self.console.print("[red]Error: Missing 'name' or 'periodicity'.[/red]")
                return
            if name in self.data["habits"]:
                self.console.print(f"[red]Habit '{name}' already exists![/red]")
                return

            self.data["habits"][name] = {
                "periodicity": periodicity,
                "created_at": datetime.now().isoformat()
            }
            self.save_data()
            self.console.print(f"[green]Habit '{name}' added successfully![/green]")
        except Exception as e:
            self.console.print(f"[red]Error adding habit: {e}[/red]")

    def check_habit(self, name: str):
        try:
            if name not in self.data["habits"]:
                self.console.print(f"[red]Habit '{name}' not found![/red]")
                return
            if name not in self.data["logs"]:
                self.data["logs"][name] = []
            self.data["logs"][name].append(datetime.now().isoformat())
            self.save_data()
            self.console.print(f"[green]Checked off '{name}' for today![/green]")
        except Exception as e:
            self.console.print(f"[red]Error checking habit: {e}[/red]")

    def list_habits(self):
        """
        The method that the Typer `list` command calls.
        Make sure the name is EXACTLY `list_habits`.
        """
        try:
            table = Table(title="Tracked Habits")
            table.add_column("Name", style="cyan")
            table.add_column("Periodicity", style="magenta")
            table.add_column("Created At", style="green")

            for name, habit in self.data["habits"].items():
                table.add_row(name, habit["periodicity"], habit["created_at"])

            self.console.print(table)
        except Exception as e:
            self.console.print(f"[red]Error listing habits: {e}[/red]")

    def streaks(self):
        try:
            table = Table(title="Habit Streaks")
            table.add_column("Habit", style="cyan")
            table.add_column("Streak (days/weeks)", style="magenta")

            for name, logs in self.data.get("logs", {}).items():
                if name not in self.data["habits"]:
                    continue  # skip logs for habits that don't exist

                sorted_logs = sorted([datetime.fromisoformat(log) for log in logs], reverse=True)
                if not sorted_logs:
                    table.add_row(name, "0")
                    continue

                streak = 1
                prev_date = sorted_logs[0]
                for log in sorted_logs[1:]:
                    diff = (prev_date - log).days
                    # daily habit -> needs exactly 1 day difference
                    if self.data["habits"][name]["periodicity"] == "daily" and diff == 1:
                        streak += 1
                    # weekly habit -> up to 7 days difference
                    elif self.data["habits"][name]["periodicity"] == "weekly" and diff <= 7:
                        streak += 1
                    else:
                        break
                    prev_date = log

                table.add_row(name, str(streak))

            self.console.print(table)
        except Exception as e:
            self.console.print(f"[red]Error calculating streaks: {e}[/red]")

    def delete_habit(self, name: str):
        try:
            if name in self.data["habits"]:
                del self.data["habits"][name]
                if name in self.data["logs"]:
                    del self.data["logs"][name]
                self.save_data()
                self.console.print(f"[red]Habit '{name}' deleted.[/red]")
            else:
                self.console.print(f"[red]Habit '{name}' not found![/red]")
        except Exception as e:
            self.console.print(f"[red]Error deleting habit: {e}[/red]")

    def summary(self):
        try:
            total_habits = len(self.data.get("habits", {}))
            total_checkins = sum(len(logs) for logs in self.data.get("logs", {}).values())

            self.console.print(f"[yellow]Total habits:[/yellow] {total_habits}")
            self.console.print(f"[green]Total check-ins:[/green] {total_checkins}")
        except Exception as e:
            self.console.print(f"[red]Error generating summary: {e}[/red]")

    def reminder(self):
        try:
            today = datetime.now().date()
            pending_habits = []

            for habit, details in self.data.get("habits", {}).items():
                # No logs => definitely pending
                if habit not in self.data.get("logs", {}):
                    pending_habits.append(habit)
                    continue

                logs = self.data["logs"][habit]
                if not logs:
                    pending_habits.append(habit)
                    continue

                last_logged = datetime.fromisoformat(logs[-1]).date()

                if details["periodicity"] == "daily" and last_logged < today:
                    pending_habits.append(habit)

                elif details["periodicity"] == "weekly":
                    # if more than 7 days since last log
                    if (today - last_logged).days > 7:
                        pending_habits.append(habit)

            if pending_habits:
                self.console.print("[red]You have pending habits to complete![/red]")
                for habit in pending_habits:
                    self.console.print(f"- {habit}")
            else:
                self.console.print("[green]All habits are up to date![/green]")
        except Exception as e:
            self.console.print(f"[red]Error generating reminders: {e}[/red]")

    def dashboard(self):
        try:
            # If no logs, display message
            if not self.data.get("logs"):
                self.console.print("[yellow]No habit logs to display on dashboard.[/yellow]")
                return

            habits = list(self.data["logs"].keys())
            checkins = [len(logs) for logs in self.data["logs"].values()]

            if not habits:
                self.console.print("[yellow]No habits to show in dashboard.[/yellow]")
                return

            plt.figure(figsize=(10, 5))
            plt.barh(habits, checkins, color='blue')
            plt.xlabel("Number of Check-ins")
            plt.ylabel("Habits")
            plt.title("Habit Progress Overview")
            plt.show()
        except Exception as e:
            self.console.print(f"[red]Error displaying dashboard: {e}[/red]")

    def details(self, name: str):
        try:
            if name not in self.data.get("habits", {}):
                self.console.print(f"[red]Habit '{name}' not found![/red]")
                return

            logs = self.data.get("logs", {}).get(name, [])
            last_checked = logs[-1] if logs else "Never"

            self.console.print(f"[cyan]Habit:[/cyan] {name}")
            self.console.print(f"[yellow]Periodicity:[/yellow] {self.data['habits'][name]['periodicity']}")
            self.console.print(f"[green]Last checked-in:[/green] {last_checked}")
        except Exception as e:
            self.console.print(f"[red]Error displaying details for habit '{name}': {e}[/red]")

    def fill_data(self):
        """
        Populate fake data for testing and demonstration.
        """
        try:
            # Clear existing data (optional)
            # self.data = {"habits": {}, "logs": {}}

            sample_habits = [
                ("Workout", "daily"),
                ("ReadBook", "daily"),
                ("WaterPlants", "daily"),
                ("GuitarPractice", "daily"),
                ("WeeklyGrocery", "weekly"),
                ("PayBills", "weekly")
            ]

            # Add sample habits if not present
            for (habit_name, period) in sample_habits:
                if habit_name not in self.data["habits"]:
                    self.data["habits"][habit_name] = {
                        "periodicity": period,
                        "created_at": datetime.now().isoformat()
                    }
                if habit_name not in self.data["logs"]:
                    self.data["logs"][habit_name] = []

            # Generate random check-ins
            # e.g., for the past 15 days
            for habit_name in self.data["habits"]:
                # random number of check-ins
                random_days = random.randint(0, 10)
                base_date = datetime.now()
                for i in range(random_days):
                    day_offset = random.randint(1, 15)
                    log_date = base_date - timedelta(days=day_offset)
                    log_str = log_date.isoformat()
                    self.data["logs"][habit_name].append(log_str)

            self.save_data()
            self.console.print("[green]Fake data added successfully![/green]")
        except Exception as e:
            self.console.print(f"[red]Error filling data: {e}[/red]")

    def reset_all(self):
        """
        Reset the entire habit system (delete habits and logs).
        """
        try:
            self.data = {"habits": {}, "logs": {}}
            self.save_data()
            self.console.print("[red]System has been reset. All habits and logs removed.[/red]")
        except Exception as e:
            self.console.print(f"[red]Error resetting system: {e}[/red]")

####################################
# Typer CLI Definition
####################################
app = typer.Typer()
habit_tracker = HabitTracker()

@app.command()
def add(
    name: str = typer.Argument(..., help="Name of the habit"),
    periodicity: str = typer.Argument(..., help="Periodicity of the habit (daily/weekly)")
):
    """Add a new habit with a given periodicity (daily, weekly)."""
    try:
        habit_tracker.add_habit(name, periodicity)
    except Exception as e:
        handle_error(e, "Failed to add the habit")
        raise typer.Exit(1)

@app.command()
def check(
    name: str = typer.Argument(..., help="Name of the habit to check")
):
    """Mark a habit as completed today."""
    try:
        habit_tracker.check_habit(name)
    except Exception as e:
        handle_error(e, "Failed to check the habit")
        raise typer.Exit(1)

@app.command()
def list():
    """Show all tracked habits."""
    try:
        habit_tracker.list_habits()
    except Exception as e:
        handle_error(e, "Failed to list habits")
        raise typer.Exit(1)

@app.command()
def streaks():
    """Show habit streaks and broken habits."""
    try:
        habit_tracker.streaks()
    except Exception as e:
        handle_error(e, "Failed to calculate streaks")
        raise typer.Exit(1)

@app.command()
def delete(
    name: str = typer.Argument(..., help="Name of the habit to delete")
):
    """Remove a habit from tracking."""
    try:
        habit_tracker.delete_habit(name)
    except Exception as e:
        handle_error(e, "Failed to delete the habit")
        raise typer.Exit(1)

@app.command()
def welcome():
    """Show the welcome message."""
    try:
        habit_tracker.show_welcome_message()
    except Exception as e:
        handle_error(e, "Failed to display welcome message")
        raise typer.Exit(1)

@app.command()
def summary():
    """Show analytics and performance summary."""
    try:
        habit_tracker.summary()
    except Exception as e:
        handle_error(e, "Failed to display summary")
        raise typer.Exit(1)

@app.command()
def reminder():
    """Show pending habits that need completion today."""
    try:
        habit_tracker.reminder()
    except Exception as e:
        handle_error(e, "Failed to display reminders")
        raise typer.Exit(1)

@app.command()
def dashboard():
    """Display a graphical analysis of habit tracking."""
    try:
        habit_tracker.dashboard()
    except Exception as e:
        handle_error(e, "Failed to display dashboard")
        raise typer.Exit(1)

@app.command()
def details(
    name: str = typer.Argument(..., help="Name of the habit to show details")
):
    """Show details about a specific habit."""
    try:
        habit_tracker.details(name)
    except Exception as e:
        handle_error(e, "Failed to display habit details")
        raise typer.Exit(1)

##########################
# New Commands for Testing
##########################

@app.command()
def fill():
    """Populate fake data for testing/demo."""
    try:
        habit_tracker.fill_data()
    except Exception as e:
        handle_error(e, "Failed to fill data")
        raise typer.Exit(1)

@app.command()
def reset():
    """Reset the entire system (remove all habits/logs)."""
    try:
        habit_tracker.reset_all()
    except Exception as e:
        handle_error(e, "Failed to reset the system")
        raise typer.Exit(1)

####################################
# Main Entry
####################################

if __name__ == "__main__":
    app()
