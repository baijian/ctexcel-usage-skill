"""Validate shared Hub metadata and expose it to GitHub Actions."""

import os
import re
from pathlib import Path

import yaml

text = Path("SKILL.md").read_text(encoding="utf-8")
parts = text.split("---", 2)
if len(parts) != 3 or parts[0].strip():
    raise SystemExit("SKILL.md must start with YAML frontmatter")
metadata = yaml.safe_load(parts[1])
for key in ("name", "slug", "displayName", "version", "summary", "description", "license"):
    value = metadata.get(key)
    if not isinstance(value, str) or not value.strip() or "\n" in value:
        raise SystemExit(f"Invalid or missing metadata: {key}")
if metadata["slug"] != metadata["name"] or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["slug"]):
    raise SystemExit("Skill name and slug must match and use kebab-case")
if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", metadata["version"]):
    raise SystemExit("Invalid release version")
if os.environ.get("GITHUB_REF_TYPE") == "tag" and os.environ.get("GITHUB_REF_NAME") != "v" + metadata["version"]:
    raise SystemExit("Tag does not match SKILL.md version")

values = {"version": metadata["version"], "slug": metadata["slug"], "name": metadata["displayName"]}
output = "".join(f"{key}={value}\n" for key, value in values.items())
if os.environ.get("GITHUB_OUTPUT"):
    with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as stream:
        stream.write(output)
print(output, end="")
