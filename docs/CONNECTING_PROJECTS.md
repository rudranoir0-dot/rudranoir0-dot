# Connect project repositories

The realm only receives events from other repositories when you configure them.

1. In each project repository, create a repository secret named REALM_DISPATCH_TOKEN.
2. Use a fine-grained token limited to rudranoir0-dot/rudranoir0-dot with the minimum repository permissions required to dispatch an event.
3. Add this workflow to the project repository as .github/workflows/notify-realm.yml:

```yaml
name: Notify the Living Realm
on:
  release:
    types: [published]
jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Send release event
        env:
          GH_TOKEN: ${{ secrets.REALM_DISPATCH_TOKEN }}
          PROJECT_URL: ${{ github.event.repository.html_url }}
        run: |
          curl --fail-with-body --request POST \
            --url "https://api.github.com/repos/rudranoir0-dot/rudranoir0-dot/dispatches" \
            --header "Accept: application/vnd.github+json" \
            --header "Authorization: Bearer $GH_TOKEN" \
            --header "X-GitHub-Api-Version: 2022-11-28" \
            --data "{\"event_type\":\"project_released\",\"client_payload\":{\"repository\":\"$PROJECT_URL\"}}"
```

A published release upgrades the matching registered building by one level, up to level 5. A release does not automatically mark a project completed. The registry remains the source of truth.

Never put tokens in source files or commit them to Git.
