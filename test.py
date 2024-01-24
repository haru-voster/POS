import subprocess
import os
from datetime import datetime, timedelta
import random

def backdate_commit(date_str, commit_message):
    """
    Creates a backdated commit in the current Git repository.

    :param date_str: Backdated timestamp in the format "YYYY-MM-DD HH:MM:SS".
    :param commit_message: Commit message for the backdated commit.
    """
    try:
        # Get the current working directory (assumes it's the Git repo)
        repo_path = os.getcwd()

        # Ensure it's a valid Git repository
        if not os.path.exists(os.path.join(repo_path, ".git")):
            print("Error: Current directory is not a valid Git repository.")
            return

        # Stage changes
        subprocess.run(["git", "add", "."], check=True)

        # Set the GIT_AUTHOR_DATE and GIT_COMMITTER_DATE
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = date_str
        env["GIT_COMMITTER_DATE"] = date_str

        # Commit the changes
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            check=True,
            env=env
        )

        print(f"Backdated commit created successfully with date: {date_str}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def generate_random_datetime(year, month):
    """
    Generate a random date and time within the specified year and month.

    :param year: Year for the random date.
    :param month: Month for the random date.
    :return: Random datetime as a string in "YYYY-MM-DD HH:MM:SS" format.
    """
    day = random.randint(1, 28)  # To avoid issues with months having fewer days
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

def get_random_commit_message():
    """
    Generate a random commit message related to Python and Qt restaurant billing system.
    """
    messages = [
        "Added table management feature",
        "Improved item category handling",
        "Fixed bugs in billing logic",
        "Updated UI for better usability",
        "Optimized database queries for performance",
        "Integrated discount feature for promotions",
        "Enhanced reporting module",
        "Implemented order tracking functionality",
        "Fixed layout issues in the billing screen",
        "Added support for new payment methods"
    ]
    return random.choice(messages)

def create_random_commits(start_date, end_date):
    """
    Creates backdated commits on random days between start_date and end_date.

    :param start_date: Start date in the format "YYYY-MM-DD".
    :param end_date: End date in the format "YYYY-MM-DD".
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    current_date = start

    while current_date <= end:
        year = current_date.year
        month = current_date.month

        # Generate a random number of commits for the month (5-10 commits)
        commit_count = random.randint(5, 10)
        for _ in range(commit_count):
            date_str = generate_random_datetime(year, month)
            commit_message = get_random_commit_message()
            backdate_commit(date_str, commit_message)

        # Move to the next month
        if month == 12:
            current_date = datetime(year + 1, 1, 1)
        else:
            current_date = datetime(year, month + 1, 1)

if __name__ == "__main__":
    # Start date
    start_date = "2024-01-01"
    # End date (current date)
    end_date = datetime.now().strftime("%Y-%m-%d")

    create_random_commits(start_date, end_date)
