from urllib import request
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
    args = sys.argv.copy()
    username = args[1]
    request = request.urlopen(f"https://api.github.com/users/{username}/events")
    data = json.loads(request.read())
    display_activity(data)
