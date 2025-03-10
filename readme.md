# Habit Tracker HCLI

## Introduction
The Habit Tracker HCLI is a command-line application that helps users track their habits efficiently. It allows users to add, check off, and analyze their habits over time using a simple and interactive HCLI.

## Features
- Add daily or weekly habits
- Check habits as completed
- View current streaks
- Show reminders for pending habits
- Generate a summary of analytics
- Display a graphical dashboard
- Store user preferences and habit data in JSON format

## Installation
Ensure you have Python installed, then install the required dependencies:
```sh
pip install -r requirements.txt
```
Also, verify that the config.json file is configured with the project's root directory.

## Usage
You can run the application using the following commands, or alternatively, you can run the `init.vbs` script to launch the program automatically with:

```sh
cscript init.vbs
```

OR Run the application using any HCLI command in the root path:
Also, verify that the config.json file is configured with the project's root directory!

### Initial Setup
Run any command to start, the application will ask you for a username to start.

```sh
python main.py --help
```
Also, verify that the config.json file is configured with the project's root directory!
### Habit Management
```sh
python main.py add "Workout" daily
python main.py check "Workout"
python main.py list_habits
python main.py streaks
python main.py reminder
python main.py summary
```

### Configuration
If you want to migrate the software to a different location, use the config commands to update the `config.json`, `habits.json`, and `user.json` file locations accordingly.

```sh
python main.py config --show
python main.py config --data-file habits.json
```

### Dashboard
```sh
python main.py dashboard
```

### Reset Data
```sh
python main.py reset
```

## Running Unit Tests
This project includes a **unit test suite** to verify the core functionality of the Habit Tracker CLI. We use **pytest** for testing. To run the tests:

### **1. Install Dependencies**
Make sure you have all required packages installed:
```sh
pip install -r requirements.txt
```

### **2. Running Tests**
Run all tests:
```sh
pytest
```
Or:
```sh
python -m pytest
```

#### Run a Specific Test File:
```sh
pytest tests/test_habit_tracker.py
```

## Project Repository
You can find the latest source code, contribute, or report issues at:
[GitHub Repository](https://github.com/alemxral/HCLI.git)

## License
This project is licensed under the MIT License.

