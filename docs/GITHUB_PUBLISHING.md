# Publishing to GitHub

## Before making the repository public

1. Run `git status --short` and inspect every tracked file.
2. Confirm no media, models, logs, cookies, tokens, or personal paths are staged.
3. Run `python scripts/validate_project.py .`.
4. Run the shell-script syntax tests documented below.
5. Confirm that the MIT license remains appropriate for the publication.
6. Replace placeholder repository and contact text.
7. Review third-party names and screenshots in documentation.

The repository uses the MIT License for its original code and documentation.
That license does not grant rights to project source media or quoted third-party
works.

## Suggested local checks

```bash
nix develop --command python scripts/validate_project.py .
nix develop --command python -m compileall -q scripts
shellcheck scripts/*.sh tests/*.sh
actionlint
git diff --check
```

## Create the GitHub repository later

After reviewing and committing locally:

```bash
gh repo create documentary-timeline-template \
  --source . \
  --public \
  --push
```

Then enable **Template repository** in the GitHub repository settings. Future
projects can use GitHub's “Use this template” action or clone the repository and
run `scripts/configure_project.py`.

Do not run the publish command until the owner has chosen visibility, license,
repository name, and GitHub organization or account.
