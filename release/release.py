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
    "slack_team_id": env('SLACK_TEAM_ID'),
    "slack_channel_id": env('SLACK_CHANNEL_ID', ''),
    "key": env('DIBS_KEY', '')
}

if env('DIBS_FORCE'):
    del payload['key']
    payload['force'] = True

if not env('DIBS_KEY', '') and not env('DIBS_FORCE', ''):
    print(f"Error: Must supply either Slack Key or Force argument")
    sys.exit(1)

response = requests.post(
    "https://conchable.com/release",
    headers={"X-Api-Key": env('DIBS_API_KEY')},
    json=payload
)

result = response.json()
code = result.get("code", "")

if code in ("released", "releasedgone", "releasedgonenobearer"):
    print(f"Released {env('DIBS_QUEUE')} {code}", file=sys.stderr)
    sys.exit(0)

elif code in ("notreleased", "noconch"):
    print(f"Not queued in {env('DIBS_QUEUE')} {code}", file=sys.stderr)
    sys.exit(0)

else:
    print(f"Error: {response.text}")
    sys.exit(1)
