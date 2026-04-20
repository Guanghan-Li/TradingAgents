import os
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_load_project_dotenv_finds_repo_env_outside_cwd(tmp_path, monkeypatch):
    from tradingagents.env import load_project_dotenv

    repo_root = tmp_path / "repo"
    package_root = repo_root / "tradingagents"
    package_root.mkdir(parents=True)
    env_path = repo_root / ".env"
    env_path.write_text("OPENAI_API_KEY=test-key\n", encoding="utf-8")

    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()

    monkeypatch.chdir(outside_dir)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    loaded_path = load_project_dotenv(start_dir=package_root)

    assert loaded_path == env_path
    assert os.environ["OPENAI_API_KEY"] == "test-key"


def test_load_project_dotenv_merges_parent_repo_env_without_overriding_worktree(tmp_path, monkeypatch):
    from tradingagents.env import load_project_dotenv

    repo_root = tmp_path / "repo"
    worktree_root = repo_root / ".worktrees" / "production"
    package_root = worktree_root / "tradingagents"
    package_root.mkdir(parents=True)

    root_env = repo_root / ".env"
    root_env.write_text("FRED_API_KEY=fred-key\nOPENAI_API_KEY=root-openai\n", encoding="utf-8")

    worktree_env = worktree_root / ".env"
    worktree_env.write_text("OPENAI_API_KEY=worktree-openai\n", encoding="utf-8")

    monkeypatch.chdir(worktree_root)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("FRED_API_KEY", raising=False)

    loaded_path = load_project_dotenv(start_dir=package_root)

    assert loaded_path == worktree_env
    assert os.environ["OPENAI_API_KEY"] == "worktree-openai"
    assert os.environ["FRED_API_KEY"] == "fred-key"
