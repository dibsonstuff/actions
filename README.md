
# Dibs On Stuff GitHub Actions

GitHub Actions for [Dibs On Stuff](https://dibsonstuff.com), allowing CI/CD pipelines to queue for shared resources and release them when finished.

Dibs provides a simple way to coordinate access to resources such as Terraform stacks, staging environments, test infrastructure and other things that cannot safely be used by multiple deployments at the same time.

## Quick start

The basic pattern is:

```text
        Dibs Seize
             |
             v
       Wait for your turn
             |
             v
        Do your work
             |
             v
       Dibs Release
```

A typical workflow looks like this:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Seize staging
        id: dibs
        uses: dibsonstuff/actions/seize@v1
        with:
          queue: staging
          slack_team: mycompany
          slack_team_id: T0123456789
          slack_username: ${{ github.actor }}
          duration: 1h
        env:
          DIBS_API_KEY: ${{ secrets.DIBS_API_KEY }}

      - name: Deploy
        run: |
          terraform apply -auto-approve

      - name: Release staging
        if: always()
        uses: dibsonstuff/actions/release@v1
        with:
          queue: staging
          slack_team: mycompany
          slack_team_id: T0123456789
          slack_key: ${{ steps.dibs.outputs.release-key }}
        env:
          DIBS_API_KEY: ${{ secrets.DIBS_API_KEY }}
```

The `if: always()` on the release step ensures that the resource is released even if the deployment fails.


## Authentication

Your Dibs API key should be stored as a GitHub Actions secret.

In the repository containing the workflow, go to:

**Settings → Secrets and variables → Actions**

Create a repository secret named:

```text
DIBS_API_KEY
```

The key is then supplied to the Actions with:

```yaml
env:
  DIBS_API_KEY: ${{ secrets.DIBS_API_KEY }}
```

Do not put the API key directly in the workflow file.

## Seize

The Seize action acquires a position in a Dibs queue.

```yaml
- name: Seize staging
  id: dibs
  uses: dibsonstuff/actions/seize@v1
  with:
    queue: staging
    slack_team: mycompany
    slack_team_id: T0123456789
    slack_username: ${{ github.actor }}
    duration: 1h
  env:
    DIBS_API_KEY: ${{ secrets.DIBS_API_KEY }}
```

### Inputs

| Input              | Required | Description                                              |
| ------------------ | -------- | -------------------------------------------------------- |
| `queue`            | Yes      | Dibs queue to acquire                                    |
| `slack_team`       | Yes      | Slack short name for your organisation                   |
| `slack_team_id`    | Yes      | Slack Team ID for your organisation                      |
| `slack_username`   | Yes      | Slack username of the person entering the queue          |
| `slack_channel_id` | No       | Slack channel ID for queue notifications                 |
| `duration`         | No       | How long to remain queue leader before automatic release |

### Release key

When Seize succeeds, it produces a `release-key` output.

The output is accessed using the step ID:

```yaml
id: dibs
```

and:

```yaml
${{ steps.dibs.outputs.release-key }}
```

This key identifies the position acquired by the Seize operation and is passed to the Release action.

## Release

Release removes the current user from the Dibs queue.

```yaml
- name: Release staging
  if: always()
  uses: dibsonstuff/actions/release@v1
  with:
    queue: staging
    slack_team: mycompany
    slack_team_id: T0123456789
    slack_key: ${{ steps.dibs.outputs.release-key }}
  env:
    DIBS_API_KEY: ${{ secrets.DIBS_API_KEY }}
```

### Inputs

| Input              | Required | Description                                              |
| ------------------ | -------- | -------------------------------------------------------- |
| `queue`            | Yes      | Dibs queue to remove the user from                       |
| `slack_team`       | Yes      | Slack short name for your organisation                   |
| `slack_team_id`    | Yes      | Slack Team ID for your organisation                      |
| `slack_channel_id` | No       | Slack channel ID for queue notifications                 |
| `slack_key`        | No       | Release key returned by the Seize action                 |
| `force`            | No       | Force the current queue leader off without a release key |

Normally you should use the release key returned by Seize.

## Using force release

A force release can be used when you do not have the release key:

```yaml
- name: Force release staging
  if: always()
  uses: dibsonstuff/actions/release@v1
  with:
    queue: staging
    slack_team: mycompany
    slack_team_id: T0123456789
    force: true
  env:
    DIBS_API_KEY: ${{ secrets.DIBS_API_KEY }}
```

Force removes the current queue leader regardless of who it is.


## Terraform example

Dibs is particularly useful when multiple CI jobs share Terraform state or other deployment infrastructure.

```yaml
jobs:
  terraform:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3

      - name: Seize Terraform environment
        id: dibs
        uses: dibsonstuff/actions/seize@v1
        with:
          queue: terraform-production
          slack_team: mycompany
          slack_team_id: T0123456789
          slack_username: ${{ github.actor }}
          duration: 2h
        env:
          DIBS_API_KEY: ${{ secrets.DIBS_API_KEY }}

      - name: Terraform apply
        run: terraform apply -auto-approve

      - name: Release Terraform environment
        if: always()
        uses: dibsonstuff/actions/release@v1
        with:
          queue: terraform-production
          slack_team: mycompany
          slack_team_id: T0123456789
          slack_key: ${{ steps.dibs.outputs.release-key }}
        env:
          DIBS_API_KEY: ${{ secrets.DIBS_API_KEY }}
```

## Why Dibs?

Terraform can protect its state from concurrent modification, but it does not necessarily stop people from competing for the same underlying environment.

Dibs adds a human-level queue around shared resources.

Instead of:

```text
"I'm deploying staging. Don't touch it."
```

your pipeline can acquire the resource explicitly:

```text
CI job → Dibs → staging
             ↓
          waiting...
             ↓
          acquired
             ↓
       deployment
             ↓
          released
```

The result is that the lock becomes part of the deployment process rather than an informal agreement between developers.

## Versioning

Actions should be referenced using a version tag:

```yaml
uses: dibsonstuff/actions/seize@v1
```

and:

```yaml
uses: dibsonstuff/actions/release@v1
```

The `v1` release will receive backwards-compatible fixes and improvements. Breaking changes will be introduced under a new major version.

## License

See [LICENSE](LICENSE).

