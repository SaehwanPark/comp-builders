from pathlib import Path


def test_public_docs_exist() -> None:
  root = Path(__file__).resolve().parents[1]
  for filename in [
    "README.md",
    "QUICKSTART.md",
    "USER_GUIDE.md",
    "API_REFERENCE.md",
    "ARCHITECTURE.md",
    "CHANGELOG.md",
    "LICENSE",
    "docs/railway-oriented-programming.md",
  ]:
    assert (root / filename).exists()


def test_two_space_indentation_config_exists() -> None:
  root = Path(__file__).resolve().parents[1]
  editorconfig = (root / ".editorconfig").read_text(encoding="utf-8")
  ruff_config = (root / "ruff.toml").read_text(encoding="utf-8")

  assert "indent_size = 2" in editorconfig
  assert "tab_width = 2" in editorconfig
  assert "indent-width = 2" in ruff_config
