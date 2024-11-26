from urllib import request, error
import sys
import json


def display_activity(events: list[dict]) -> None:
    if not events:
        print("No recent activity found.")
        return

    for event in events:
        action = None
        if event["type"] == "PushEvent":
            commit_count = len(event["payload"]["commits"])
            action = f"Pushed {commit_count} commit(s) to {event['repo']['name']}"
        elif event["type"] == "IssuesEvent":
            action = f"{event['payload']['action'].capitalize()} an issue in {event['repo']['name']}"
        elif event["type"] == "WatchEvent":
            action = f"Starred {event['repo']['name']}"
        elif event["type"] == "ForkEvent":
            action = f"Forked {event['repo']['name']}"
        elif event["type"] == "CreateEvent":
            action = (
                f"Created {event['payload']['ref_type']} in {event['repo']['name']}"
            )
        else:
            action = f"{event['type'].replace('Event', '')} in {event['repo']['name']}"

        print(f"- {action}")


if __name__ == "__main__":
    try:
        args = sys.argv.copy()
        if len(args) < 2:
            print("Usage: github-user-activity <github-username>")
            sys.exit(1)

        username = args[1]
        url = f"https://api.github.com/users/{username}/events"
        response = request.urlopen(url)
        data = json.loads(response.read())
        display_activity(data)

    except error.HTTPError as e:
        if e.code == 403:
            print("Rate limit exceeded! Try again later.")
        elif e.code == 404:
            print(f"User '{username}' not found.")
        else:
            print(f"HTTPError: {e.code} - {e.reason}")
    except error.URLError as e:
        print(f"Failed to fetch data: {e.reason}")
    except json.JSONDecodeError:
        print("Failed to parse JSON response.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
