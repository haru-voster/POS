import subprocess
import os

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
    # Backdated timestamp
    backdate = "2024-11-19 12:00:00"

    # Commit message
    message = "Ui Tweaks"

    backdate_commit(backdate, message)
