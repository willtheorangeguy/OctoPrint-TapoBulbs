# CI/CD

GitHub Actions tests the plugin and delegates documentation builds to the same
shared MkDocs repository used by OctoPrint-HomeAssistantPower.

## Test workflow

`.github/workflows/test.yml` runs on pushes and pull requests. Its matrix uses
Python 3.9 and 3.12, installs OctoPrint, installs the plugin with development
extras, and runs pytest.

The local equivalent is:

```bash
python -m pip install OctoPrint
python -m pip install --no-build-isolation -e ".[develop]"
python -m pytest
```

## Documentation lint

`.github/workflows/docs-lint.yml` calls the reusable documentation lint
workflow on pull requests that affect the site, plugin source, or docs tooling.
It performs markdown checks, a strict MkDocs build, and external-link checks.

Run the strict local build on Windows with:

```powershell
.\scripts\docs-serve.ps1 -Build
```

## Documentation deployment

`.github/workflows/docs.yml` calls the reusable build workflow on changes to
`main`. That workflow publishes the MkDocs output to GitHub Pages. The caller
grants `contents: read`, `pages: write`, and `id-token: write`.

## Plugin releases

The source contains an OctoPrint software-update hook pointed at GitHub
releases. Publishing a tag and matching GitHub release makes that version
discoverable to installed instances. Update `plugin_version` and the archive
URL shown in the docs before publishing a release.
