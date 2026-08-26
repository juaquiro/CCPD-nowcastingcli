# mkdocs_hooks.py
# MkDocs build hooks — keep docs in sync with pyproject.toml (single source
# of truth for the version) instead of hand-editing version strings.
import tomllib
from datetime import date


def on_config(config):
    """Populate extra.project_version / extra.build_date and the footer copyright.

    MkDocs does not re-run the "copyright" config value through Jinja, so it's
    set here as an already-formatted string rather than a template placeholder.
    """
    with open("pyproject.toml", "rb") as f:
        meta = tomllib.load(f)
    version = meta["project"]["version"]
    build_date = date.today().isoformat()

    config["extra"]["project_version"] = version
    config["extra"]["build_date"] = build_date
    config["copyright"] = f"NowcastingCLI v{version} — Built {build_date}"
    return config


def on_page_markdown(markdown, page, config, files):
    """Substitute {{ project_version }} / {{ build_date }} in page source.

    Plain MkDocs (without mkdocs-macros-plugin) does not evaluate Jinja
    expressions inside markdown content, so this does the substitution
    manually using the values on_config() stored in config["extra"].
    """
    return (
        markdown
        .replace("{{ project_version }}", config["extra"]["project_version"])
        .replace("{{ build_date }}", config["extra"]["build_date"])
    )
