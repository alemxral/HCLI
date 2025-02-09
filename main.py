import typer
import json
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
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
# Config Manager
####################################
class ConfigManager:
    CONFIG_FILE = "config.json"

    def __init__(self):
        # We store rootPath by default, plus the data_file and user_file.
        self.config_data = {
            "rootPath": "",
            "data_file": "habits.json",
            "user_file": "user.json"
        }
        self.load_config()

    def ensure_config(self):
        """Ensure the config.json file exists, setting default root path if missing."""
        if not os.path.exists(self.CONFIG_FILE):
            root_path = os.getcwd()
            default_config = {"rootPath": root_path}
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(default_config, f, indent=4)
            print(f"Config file created with root path: {root_path}")

    def load_config(self):
        try:
            with open(self.CONFIG_FILE, "r") as f:
                file_conf = json.load(f)
            for k in ["rootPath", "data_file", "user_file"]:
                if k in file_conf:
                    self.config_data[k] = file_conf[k]
        except FileNotFoundError:
            # no config, that's fine
            pass
        except Exception as e:
            typer.echo(f"[red]Error loading config: {e}[/red]")

    def save_config(self):
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(self.config_data, f, indent=4)
        except Exception as e:
            typer.echo(f"[red]Error saving config: {e}[/red]")

    def set_root_path(self, path: str):
        self.config_data["rootPath"] = path
        self.save_config()

    def set_data_file(self, path: str):
        self.config_data["data_file"] = path
        self.save_config()

    def set_user_file(self, path: str):
        self.config_data["user_file"] = path
        self.save_config()

    def show(self):
        typer.echo("Current Configuration:")
        for k, v in self.config_data.items():
            typer.echo(f"- {k}: {v}")

####################################
# Main HabitTracker class
####################################
class HabitTracker:
    def __init__(self, config: ConfigManager):
        self.console = Console()
        self.config = config
        self.config_manager = config_manager

        # Combine root path if the user wants to store data there
        root = self.config.config_data["rootPath"]
        dataFile = self.config.config_data["data_file"]
        userFile = self.config.config_data["user_file"]

        if root:
            if not os.path.isabs(dataFile):
                dataFile = os.path.join(root, os.path.basename(dataFile))
            if not os.path.isabs(userFile):
                userFile = os.path.join(root, os.path.basename(userFile))

        self.DATA_FILE = dataFile
        self.USER_FILE = userFile

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
            d = os.path.dirname(self.DATA_FILE)
            if d and not os.path.exists(d):
                os.makedirs(d)

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
            # Ensure config exists before proceeding
            self.config_manager.ensure_config()

            # Avoid asking twice by checking if USER_FILE already exists
            if os.path.exists(self.USER_FILE):
                return  # Exit early if user already set up

            username = self.console.input("[cyan]Enter a username to set up or change the existing username in HCLI: [/cyan]")

            ud = os.path.dirname(self.USER_FILE)
            if ud and not os.path.exists(ud):
                os.makedirs(ud)

            with open(self.USER_FILE, "w") as f:
                json.dump({"username": username}, f, indent=4)

            self.console.print(f"[green]Username '{username}' has been set successfully![/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error setting up user: {e}[/red]")


    def intro(self):
        """Explain to the user how to use the program and what it's about."""
        self.console.print("""
[cyan]Welcome to the HCLI![/cyan]

This program helps you create, track, and analyze habits. You can:
- Add daily or weekly habits,
- Check them off when done,
- View streaks and pending tasks,
- See analytics,
- And more!

[b]Command Overview:[/b]
- [green]intro[/green]: This introduction.
- [green]add[/green]: Create a new habit.
- [green]check[/green]: Mark a habit as complete.
- [green]list_habits[/green]: Show all tracked habits.
- [green]streaks[/green]: See your best streaks.
- [green]reminder[/green]: Show overdue habits.
- [green]summary[/green]: View analytics and performance.
- [green]dashboard[/green]: Show a chart (ASCII or Matplotlib).
- [green]delete[/green]: Remove a habit (or remove a single check).
- [green]details[/green]: Detailed info on a habit.
- [green]fill[/green]: Generate some fake data.
- [green]reset[/green]: Wipe everything.
- [green]config[/green]: Adjust file paths or root path.
- [green]welcome[/green]: Display a welcome message & summary.

[b]Usage Examples:[/b]
- python main.py add "Workout" daily
- python main.py list_habits
- python main.py streaks
- python main.py config --show
- python main.py config --data-file MyHabits.json

Enjoy tracking your habits!
""")

    def show_welcome_message(self):
        try:
            if self.username:
                self.console.print(
                    f"[green]Welcome back, {self.username}, to HCLI - Your Personal Habit Tracker![/green]"
                )
                self.console.print("[yellow]Stay consistent and track your progress effortlessly.[/yellow]")
                self.console.print("\n[yellow]Useful commands:")
                self.console.print("- `intro`: Brief introduction about this program")
                self.console.print("- `add <habit> <daily/weekly>`: Add a new habit")
                self.console.print("- `check <habit>`: Mark a habit as completed")
                self.console.print("- `list_habits`: Show all habits")
                self.console.print("- `streaks`: View your habit streaks")
                self.console.print("- `summary`: View analytics and performance")
                self.console.print("- `reminder`: Get reminders for pending habits")
                self.console.print("- `dashboard`: Show a graphical or CLI analysis of habits")
                self.console.print("- `delete <habit>`: Remove a habit (or a single check).")
                self.console.print("- `details <habit>`: Show detailed info about a habit")
                self.console.print("- `fill`: Populate fake data for testing.")
                self.console.print("- `reset`: Reset all habits and logs.")
                self.console.print("- `config`: Manage configuration.")
                self.console.print("\nFor more info, run: [blue]python main.py --help[/blue]")

                if hasattr(self, 'summary') and callable(getattr(self, 'summary', None)):
                    self.console.print("\n[blue]Habit Tracking Summary:[/blue]")
                    self.summary()
                else:
                    self.console.print("\n[blue]No habit tracking summary available yet.[/blue]")

                if hasattr(self, 'reminder') and callable(getattr(self, 'reminder', None)):
                    self.console.print("\n[red]Pending Habit Reminders:[/red]")
                    self.reminder()
                else:
                    self.console.print("\n[green]No pending habit reminders.[/green]")
            else:
                self.console.print("[cyan]Welcome to HCLI!")
                self.console.print("For usage info, run: [blue]python main.py --help[/blue]")
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
            self.console.print(f"[green]Habit '{name}' ({periodicity}) added successfully![/green]")
        except Exception as e:
            self.console.print(f"[red]Error adding habit: {e}[/red]")

    def check_habit(self, name: str, date_str: str = None):
        """
        Mark a habit as completed, optionally specifying a date (YYYY-MM-DD). 
        Default is today's date if no date_str is provided.
        """
        try:
            if name not in self.data["habits"]:
                self.console.print(f"[red]Habit '{name}' not found![/red]")
                return

            if date_str:
                # parse the user-provided date
                try:
                    custom_date = datetime.strptime(date_str, "%Y-%m-%d")
                    log_str = custom_date.isoformat()
                except ValueError:
                    self.console.print("[red]Invalid date format. Use YYYY-MM-DD.[/red]")
                    return
            else:
                # default to today's date/time
                log_str = datetime.now().isoformat()

            if name not in self.data["logs"]:
                self.data["logs"][name] = []
            self.data["logs"][name].append(log_str)

            self.save_data()
            period = self.data["habits"][name].get("periodicity", "daily/weekly?")
            self.console.print(f"[green]Checked off '{name}' ({period}) on {log_str}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error checking habit: {e}[/red]")

    def list_habits_cmd(self):
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
        """Show the longest streak overall and display streaks for each habit."""
        try:
            table = Table(title="Habit Streaks")
            table.add_column("Habit", style="cyan")
            table.add_column("Periodicity", style="magenta")
            table.add_column("Streak (days/weeks)", style="magenta")

            longest_streak = 0
            best_habit = None

            for name, logs in self.data.get("logs", {}).items():
                if name not in self.data["habits"]:
                    continue
                period = self.data["habits"][name].get("periodicity", "?")
                sorted_logs = sorted([datetime.fromisoformat(log) for log in logs], reverse=True)
                if not sorted_logs:
                    table.add_row(name, period, "0")
                    continue

                streak = 1
                prev_date = sorted_logs[0]
                for log in sorted_logs[1:]:
                    diff = (prev_date - log).days
                    if period == "daily" and diff == 1:
                        streak += 1
                    elif period == "weekly" and diff <= 7:
                        streak += 1
                    else:
                        break
                    prev_date = log

                if streak > longest_streak:
                    longest_streak = streak
                    best_habit = name

                table.add_row(name, period, str(streak))

            self.console.print(table)

            if best_habit:
                self.console.print(f"\n[green]Longest habit streak is {longest_streak} for habit '{best_habit}'[/green]")
            else:
                self.console.print("\n[yellow]No habits have been checked in yet.[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Error calculating streaks: {e}[/red]")

    def delete_habit(self, name: str, date_str: str = None):
        """
        Remove an entire habit if no date is specified, or remove a single check from logs for that date.
        """
        try:
            if name not in self.data["habits"]:
                self.console.print(f"[red]Habit '{name}' not found![/red]")
                return

            if date_str:
                # remove a single check for the specified date
                if name not in self.data["logs"]:
                    self.console.print("[yellow]No logs for this habit to remove.[/yellow]")
                    return
                try:
                    # parse user date
                    custom_date = datetime.strptime(date_str, "%Y-%m-%d")
                    iso_str = custom_date.isoformat()

                    # remove any matching date from logs
                    old_count = len(self.data["logs"][name])
                    self.data["logs"][name] = [
                        dt for dt in self.data["logs"][name]
                        if not dt.startswith(iso_str)
                    ]
                    new_count = len(self.data["logs"][name])
                    removed = old_count - new_count

                    self.console.print(f"[green]Removed {removed} checks dated {date_str} from '{name}'.[/green]")
                    self.save_data()
                except ValueError:
                    self.console.print("[red]Invalid date format. Use YYYY-MM-DD.[/red]")
            else:
                # remove the entire habit
                del self.data["habits"][name]
                if name in self.data["logs"]:
                    del self.data["logs"][name]
                self.save_data()
                self.console.print(f"[red]Habit '{name}' deleted entirely.[/red]")
        except Exception as e:
            self.console.print(f"[red]Error deleting habit: {e}[/red]")

    def calc_30days_checkins(self, name):
        """Calculate how many check-ins in the last 30 days for the specified habit."""
        logs = self.data.get("logs", {}).get(name, [])
        thirty_days_ago = datetime.now() - timedelta(days=30)
        count_30 = 0
        for log in logs:
            dt = datetime.fromisoformat(log)
            if dt >= thirty_days_ago:
                count_30 += 1
        return count_30

    def summary(self):
        """
        Show analytics, including:
          - total habits
          - total check-ins
          - pending habits
          - list of daily habits
          - habits user struggled with last month
        """
        try:
            total_habits = len(self.data.get("habits", {}))
            total_checkins = sum(len(logs) for logs in self.data.get("logs", {}).values())

            self.console.print(f"[yellow]Total habits:[/yellow] {total_habits}")
            self.console.print(f"[green]Total check-ins:[/green] {total_checkins}")

            pending_habits = self.get_pending_habits()
            if pending_habits:
                self.console.print("\n[red]Pending Habits (need check-in today or this week):[/red]")
                for item in pending_habits:
                    habit_name = item[0]
                    period = item[1]
                    self.console.print(f"- {habit_name} ({period})")
            else:
                self.console.print("\n[green]No pending habits for today/week![/green]")

            daily_list = [h for h, d in self.data.get("habits", {}).items() if d.get("periodicity") == "daily"]
            if daily_list:
                self.console.print("\n[blue]Current Daily Habits:[/blue]")
                for hname in daily_list:
                    self.console.print(f"- {hname}")
            else:
                self.console.print("\n[yellow]No daily habits found.[/yellow]")

            if total_habits > 0:
                struggle_list = []
                for habit, details in self.data.get("habits", {}).items():
                    checks_30 = self.calc_30days_checkins(habit)
                    struggle_list.append((habit, checks_30))

                struggle_list.sort(key=lambda x: x[1])
                min_checkin = struggle_list[0][1]
                struggled_habits = [s for s in struggle_list if s[1] == min_checkin]

                self.console.print("\n[magenta]Habits you struggled with the most last month:[/magenta]")
                for (habit_name, ccount) in struggled_habits:
                    self.console.print(f"- {habit_name} -> {ccount} check-ins in last 30 days")
            else:
                self.console.print("\n[yellow]No habits to analyze for last month struggles.[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Error generating summary: {e}[/red]")

    def get_pending_habits(self):
        pending_list = []
        try:
            today = datetime.now().date()
            for habit, details in self.data.get("habits", {}).items():
                period = details.get("periodicity", "daily")

                if habit not in self.data.get("logs", {}):
                    pending_list.append((habit, period))
                    continue

                logs = self.data["logs"][habit]
                if not logs:
                    pending_list.append((habit, period))
                    continue

                last_logged = datetime.fromisoformat(logs[-1]).date()

                if period == "daily" and last_logged < today:
                    pending_list.append((habit, period))
                elif period == "weekly":
                    if (today - last_logged).days > 7:
                        pending_list.append((habit, period))
        except Exception as e:
            self.console.print(f"[red]Error getting pending habits: {e}[/red]")
        return pending_list

    def reminder(self):
        try:
            pending_list = self.get_pending_habits()
            if pending_list:
                self.console.print("[red]You have pending habits to complete![/red]")
                for (habit_name, period) in pending_list:
                    self.console.print(f"- {habit_name} ({period})")
            else:
                self.console.print("[green]All habits are up to date![/green]")
        except Exception as e:
            self.console.print(f"[red]Error generating reminders: {e}[/red]")

    def dashboard(self, ascii_mode: bool = False):
        try:
            if not self.data.get("logs"):
                self.console.print("[yellow]No habit logs to display on dashboard.[/yellow]")
                return

            habits = list(self.data["logs"].keys())
            checkins = [len(logs) for logs in self.data["logs"].values()]

            if not habits:
                self.console.print("[yellow]No habits to show in dashboard.[/yellow]")
                return

            if ascii_mode:
                max_checkins = max(checkins)
                if max_checkins == 0:
                    self.console.print("[yellow]No check-ins to display in ASCII dashboard.[/yellow]")
                    return

                self.console.print("[cyan]ASCII Dashboard Overview[/cyan]")
                for h, c in zip(habits, checkins):
                    bar_len = int((c / max_checkins) * 40)
                    bar = "#" * bar_len
                    self.console.print(f"[blue]{h}[/blue] ({c} check-ins): [green]{bar}[/green]")
            else:
                import matplotlib.pyplot as plt
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

            habit_info = self.data["habits"][name]
            period = habit_info.get("periodicity", "daily/weekly?")

            logs = self.data.get("logs", {}).get(name, [])
            last_checked = logs[-1] if logs else "Never"

            self.console.print(f"[cyan]Habit:[/cyan] {name} ({period})")
            self.console.print(f"[yellow]Periodicity:[/yellow] {period}")
            self.console.print(f"[green]Last checked-in:[/green] {last_checked}")

            total_ci = len(logs)
            self.console.print(f"[blue]Total check-ins so far:[/blue] {total_ci}")
        except Exception as e:
            self.console.print(f"[red]Error displaying details for habit '{name}': {e}[/red]")

    def fill_data(self):
        """
        Generate fake data covering at least two months.
        """
        try:
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

            # Generate random check-ins for the past 2 months (60 days)
            for habit_name, details in self.data["habits"].items():
                # random number of check-ins (between 10 and 30 for variety)
                random_days = random.randint(10, 30)
                base_date = datetime.now()

                for _ in range(random_days):
                    day_offset = random.randint(1, 60)  # up to 60 days in the past
                    log_date = base_date - timedelta(days=day_offset)
                    log_str = log_date.isoformat()
                    self.data["logs"][habit_name].append(log_str)

            self.save_data()
            self.console.print("[green]Fake data added successfully (covering ~2 months)! Now you can test functionalities.[/green]")
        except Exception as e:
            self.console.print(f"[red]Error filling data: {e}[/red]")

    def reset_all(self):
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

config_manager = ConfigManager()
habit_tracker = HabitTracker(config_manager)

####################################
# Intro Command
####################################
@app.command("intro")
def intro():
    """Call the intro function from the HabitTracker class."""
    habit_tracker.intro()

####################################
# Config Command
####################################
@app.command("config")
def config_command(
    show: bool = typer.Option(False, "--show", help="Show current config"),
    data_file: str = typer.Option(None, "--data-file", help="Set location of habits data file"),
    user_file: str = typer.Option(None, "--user-file", help="Set location of user file"),
    root_path: str = typer.Option(None, "--root-path", help="Set a new root path."),
):
    """Manage configuration, including root path, data_file, and user_file."""
    try:
        if show:
            config_manager.show()
        if data_file:
            config_manager.set_data_file(data_file)
            typer.echo(f"Data file updated to {data_file}")
        if user_file:
            config_manager.set_user_file(user_file)
            typer.echo(f"User file updated to {user_file}")
        if root_path:
            config_manager.set_root_path(root_path)
            typer.echo(f"Root path updated to {root_path}")

        if show or data_file or user_file or root_path:
            typer.echo("Please re-run the application so changes take effect.")
    except Exception as e:
        handle_error(e, "Failed to manage config")
        raise typer.Exit(1)

####################################
# Setup User
####################################
@app.command("setup-user")
def setup_user():
    """Setup or update the username for the Habit Tracker."""
    habit_tracker.setup_user()


@app.command("change-username")
def change_username():
    """Change the existing username for the Habit Tracker."""
    try:
        new_username = habit_tracker.console.input("[cyan]Enter a new username: [/cyan]").strip()

        if not new_username:
            habit_tracker.console.print("[red]Error: Username cannot be empty![/red]")
            return

        with open(habit_tracker.USER_FILE, "w") as f:
            json.dump({"username": new_username}, f, indent=4)

        habit_tracker.console.print(f"[green]Username changed successfully to '{new_username}'![/green]")

    except Exception as e:
        habit_tracker.console.print(f"[red]Error changing username: {e}[/red]")

####################################
# Standard Commands
####################################
@app.command("list_habits")
def list_habits_cmd():
    """Show all tracked habits."""
    try:
        habit_tracker.list_habits_cmd()
    except Exception as e:
        handle_error(e, "Failed to list habits")
        raise typer.Exit(1)

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
    name: str = typer.Argument(..., help="Name of the habit to check"),
    date: str = typer.Option(None, "--date", help="Optional date in YYYY-MM-DD format for the check.")
):
    """
    Mark a habit as completed, optionally specifying a date.
    Default is today's date if no date is provided.
    """
    try:
        habit_tracker.check_habit(name, date)
    except Exception as e:
        handle_error(e, "Failed to check the habit")
        raise typer.Exit(1)

@app.command()
def streaks():
    """Show habit streaks and the overall longest streak."""
    try:
        habit_tracker.streaks()
    except Exception as e:
        handle_error(e, "Failed to calculate streaks")
        raise typer.Exit(1)

@app.command()
def delete(
    name: str = typer.Argument(..., help="Name of the habit to delete or remove a check from."),
    date: str = typer.Option(None, "--date", help="Optional date in YYYY-MM-DD to remove a single check.")
):
    """
    Remove an entire habit if no date is specified,
    or remove a single check from logs for that date if --date is provided.
    """
    try:
        habit_tracker.delete_habit(name, date)
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
    """Show analytics and performance summary (pending, daily, struggled)."""
    try:
        habit_tracker.summary()
    except Exception as e:
        handle_error(e, "Failed to display summary")
        raise typer.Exit(1)

@app.command()
def reminder():
    """Show pending habits that need completion today (mention daily/weekly)."""
    try:
        habit_tracker.reminder()
    except Exception as e:
        handle_error(e, "Failed to display reminders")
        raise typer.Exit(1)

@app.command()
def dashboard(
    ascii_mode: bool = typer.Option(False, "--ascii", help="Print ASCII chart in the console.")
):
    """Display a graphical or ASCII analysis of habit tracking."""
    try:
        habit_tracker.dashboard(ascii_mode=ascii_mode)
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
# Commands for Testing
##########################
@app.command()
def fill():
    """Populate fake data for testing/demo (covering at least 2 months)."""
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
