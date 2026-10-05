
# Dibs On Stuff GitHub Actions

### Example:


```
- name: Seize
  id: dibs
  uses: dibsonstuff/actions/seize@v1
  with:
    queue: staging
    slack_team: casio
    slack_team_id: TT1234ABCD
    slack_username: @benedictcabbagepatch
  env:
    DIBS_API_KEY: ${{ secrets.DIBS_API_KEY }}

- name: Terraform
  run: Eg: something like: terraform apply -auto-approve

- name: Release
  if: always()
  uses: dibsonstuff/actions/release@v1
  with:
    release-key: ${{ steps.dibs.outputs.release-key }}
  env:
    DIBS_API_KEY: ${{ secrets.DIBS_API_KEY }}
```
