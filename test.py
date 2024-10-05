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

# Example usage
if __name__ == "__main__":

    commit_messages = [
        "Updated item category dropdown",
        "Optimized bill generation logic",
        "Enhanced UI responsiveness",
        "Fixed bug in table reservation system",
        "Improved database indexing for speed",
        "Added tax calculation module",
        "Refactored discount logic",
        "Improved error handling in the order system",
        "Enhanced user feedback on invalid input",
        "Streamlined payment process"
    ]

    current_date = datetime.now()
    six_months_ago = current_date - timedelta(days=180)

    for _ in range(10):  # Generate 10 random commits
        # Generate a random date within the last 6 months
        random_date = six_months_ago + timedelta(days=random.randint(0, 180))
        random_time = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
        random_date_str = random_date.strftime(f"%Y-%m-%d {random_time}")

        # Choose a random commit message
        commit_message = random.choice(commit_messages)

        # Call the backdate_commit function
        backdate_commit(random_date_str, commit_message)
