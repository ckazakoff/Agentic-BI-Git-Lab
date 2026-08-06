#!/usr/bin/env python3
"""Validate the plugin marketplace in this repo.

Runs identically on a laptop (before you commit) and in CI (on a pull request).
Standard library only, no pip install, no network.

    python scripts/validate_plugins.py

Exit code 0 = everything passed, 1 = at least one error.
Output is plain ASCII on purpose - some Windows console encodings choke on
check-mark characters.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Directories that are never part of the marketplace.
SKIP_DIRS = {".git", "references", "node_modules", "__pycache__", ".venv"}

SEMVER = re.compile(r"^\d+\.\d+\.\d+")
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)

# Built from parts so this file does not match its own scan.
SECRET_PATTERNS = [
    ("GitLab PAT", re.compile("glpat" + r"-[A-Za-z0-9_\-]{20,}")),
    ("GitHub PAT", re.compile("gh" + r"[pousr]_[A-Za-z0-9]{36,}")),
    ("GitHub fine-grained PAT", re.compile("github" + r"_pat_[A-Za-z0-9_]{50,}")),
    ("Slack token", re.compile("xox" + r"[baprs]-[A-Za-z0-9\-]{10,}")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]

errors: list[str] = []
warnings: list[str] = []
checks_run = 0


def fail(where: Path | str, message: str) -> None:
    errors.append(f"{rel(where)}: {message}")


def warn(where: Path | str, message: str) -> None:
    warnings.append(f"{rel(where)}: {message}")


def rel(p: Path | str) -> str:
    try:
        return str(Path(p).resolve().relative_to(REPO)).replace("\\", "/")
    except ValueError:
        return str(p)


def load_json(path: Path) -> dict | None:
    global checks_run
    checks_run += 1
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(path, "file is missing")
    except json.JSONDecodeError as exc:
        fail(path, f"invalid JSON - {exc.msg} (line {exc.lineno}, col {exc.colno})")
    return None


def frontmatter_of(path: Path) -> dict[str, str] | None:
    """Parse the top-level `key: value` pairs of a YAML frontmatter block.

    Deliberately naive - the frontmatter in this repo is flat key/value only,
    and a naive parser keeps this script dependency-free.
    """
    global checks_run
    checks_run += 1
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    if not match:
        fail(path, "missing YAML frontmatter (the '---' block at the very top of the file)")
        return None
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.startswith("#") or line[:1].isspace():
            continue
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip().strip("\"'")
    return fields


def walk_files(root: Path):
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path


# --------------------------------------------------------------------------
# 1. marketplace manifest
# --------------------------------------------------------------------------
def check_marketplace() -> list[Path]:
    manifest_path = REPO / ".claude-plugin" / "marketplace.json"
    manifest = load_json(manifest_path)
    if manifest is None:
        return []

    for key in ("name", "owner", "plugins"):
        if key not in manifest:
            fail(manifest_path, f"missing required key '{key}'")

    plugin_dirs: list[Path] = []
    for entry in manifest.get("plugins", []):
        name = entry.get("name")
        source = entry.get("source")
        if not name or not source:
            fail(manifest_path, f"plugin entry needs both 'name' and 'source': {entry}")
            continue
        if not entry.get("description"):
            warn(manifest_path, f"plugin '{name}' has no description")
        directory = (REPO / source).resolve()
        if not directory.is_dir():
            fail(manifest_path, f"plugin '{name}' points at '{source}', which does not exist")
            continue
        plugin_dirs.append(directory)

    listed = {d.name for d in plugin_dirs}
    on_disk = {d.name for d in (REPO / "plugins").iterdir() if d.is_dir()} if (REPO / "plugins").is_dir() else set()
    for orphan in sorted(on_disk - listed):
        fail(manifest_path, f"plugins/{orphan} exists on disk but is not listed in the marketplace")

    return plugin_dirs


# --------------------------------------------------------------------------
# 2. plugin manifest
# --------------------------------------------------------------------------
def check_plugin(plugin_dir: Path) -> None:
    manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
    manifest = load_json(manifest_path)
    if manifest is None:
        return

    for key in ("name", "description", "version"):
        if not manifest.get(key):
            fail(manifest_path, f"missing required key '{key}'")

    if manifest.get("name") and manifest["name"] != plugin_dir.name:
        fail(manifest_path, f"name '{manifest['name']}' does not match its folder '{plugin_dir.name}'")

    version = manifest.get("version", "")
    if version and not SEMVER.match(str(version)):
        fail(manifest_path, f"version '{version}' is not semver (expected MAJOR.MINOR.PATCH)")


# --------------------------------------------------------------------------
# 3. skills, commands, agents
# --------------------------------------------------------------------------
def check_skills(plugin_dir: Path) -> None:
    skills_dir = plugin_dir / "skills"
    if not skills_dir.is_dir():
        return
    for skill_dir in sorted(d for d in skills_dir.iterdir() if d.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            fail(skill_dir, "a skill folder must contain a SKILL.md")
            continue
        fields = frontmatter_of(skill_md)
        if fields is None:
            continue
        name = fields.get("name")
        description = fields.get("description")
        if not name:
            fail(skill_md, "frontmatter is missing 'name'")
        elif name != skill_dir.name:
            fail(skill_md, f"frontmatter name '{name}' does not match its folder '{skill_dir.name}'")
        if not description:
            fail(skill_md, "frontmatter is missing 'description'")
        elif len(description) < 40:
            warn(
                skill_md,
                "description is very short - it is the only thing Claude sees when deciding "
                "whether to use this skill, so say when to use it",
            )


def check_markdown_dir(plugin_dir: Path, folder: str, required: tuple[str, ...]) -> None:
    directory = plugin_dir / folder
    if not directory.is_dir():
        return
    for md in sorted(directory.glob("*.md")):
        fields = frontmatter_of(md)
        if fields is None:
            continue
        for key in required:
            if not fields.get(key):
                fail(md, f"frontmatter is missing '{key}'")


# --------------------------------------------------------------------------
# 4. ${CLAUDE_PLUGIN_ROOT} references actually resolve
# --------------------------------------------------------------------------
PLUGIN_ROOT_REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_\-./]+)")


def check_plugin_root_refs(plugin_dir: Path) -> None:
    global checks_run
    for path in walk_files(plugin_dir):
        if path.suffix.lower() not in {".md", ".json", ".py", ".ps1"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for ref in set(PLUGIN_ROOT_REF.findall(text)):
            checks_run += 1
            target = plugin_dir / ref.rstrip(".,;:)")
            if target.exists():
                continue
            # Some referenced files are created by the user from a committed
            # template and are gitignored - e.g. connection.example.ps1 copied
            # to connection.ps1. Those count as present.
            template = target.with_name(f"{target.stem}.example{target.suffix}")
            if template.exists():
                continue
            fail(path, f"references ${{CLAUDE_PLUGIN_ROOT}}/{ref}, which does not exist")


# --------------------------------------------------------------------------
# 5. no secrets
# --------------------------------------------------------------------------
TEXT_SUFFIXES = {".md", ".json", ".yml", ".yaml", ".py", ".ps1", ".sh", ".sql", ".qvs", ".csv", ".txt", ".env"}


def check_secrets() -> None:
    global checks_run
    for path in walk_files(REPO):
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        checks_run += 1
        for label, pattern in SECRET_PATTERNS:
            match = pattern.search(text)
            if match:
                line = text[: match.start()].count("\n") + 1
                fail(path, f"looks like a committed {label} on line {line} - remove it and rotate the credential")


def main() -> int:
    try:
        name = json.loads(
            (REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        ).get("name", REPO.name)
    except (OSError, json.JSONDecodeError):
        name = REPO.name
    print(f"Validating {name} ...\n")

    plugin_dirs = check_marketplace()
    for plugin_dir in plugin_dirs:
        check_plugin(plugin_dir)
        check_skills(plugin_dir)
        check_markdown_dir(plugin_dir, "commands", ("description",))
        check_markdown_dir(plugin_dir, "agents", ("name", "description"))
        check_plugin_root_refs(plugin_dir)
    check_secrets()

    for message in warnings:
        print(f"  WARN  {message}")
    for message in errors:
        print(f"  FAIL  {message}")
    if warnings or errors:
        print()

    plugins = ", ".join(d.name for d in plugin_dirs) or "none"
    print(f"Plugins checked: {plugins}")
    print(f"{checks_run} checks run, {len(errors)} error(s), {len(warnings)} warning(s)")

    if errors:
        print("\nRESULT: FAIL - fix the errors above, then run this again.")
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
