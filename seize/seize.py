import os
import sys
import requests


def env(name, default=None):
    value = os.environ.get(name, default)
    if value is None:
        print(f"Missing environment var: {name}")
        sys.exit(1)
    return value


payload = {
    "conch": f"{env('SLACK_TEAM')}/{env('DIBS_QUEUE')}",
    "name": env('DIBS_USER'),
    "email": f"{env('DIBS_USER')}@{env('SLACK_TEAM')}",
    "duration": env('DIBS_DURATION'),
    "slack_team_id": env('SLACK_TEAM_ID'),
    "slack_channel_id": env('SLACK_CHANNEL_ID', '')
}

response = requests.post(
    "https://conchable.com/seize",
    headers={"X-Api-Key": env('DIBS_API_KEY')},
    json=payload
)

result = response.json()
code = result.get("code", "")

if code in ("created", "alreadybearer"):
    print(f"Claimed {env('DIBS_QUEUE')} {code}", file=sys.stderr)  # logged
    print(result.get('key', ''))  # stdout captured
    sys.exit(0)

elif code in ("added", "alreadyexists"):
    print(f"Waiting for {env('DIBS_QUEUE')} {code}", file=sys.stderr)  # logged
    print(result.get('key', ''))  # stdout captured
    sys.exit(2)

else:
    print(f"Error: {response.text}")
    sys.exit(1)
