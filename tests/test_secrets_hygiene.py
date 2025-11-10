from pathlib import Path


def test_env_file_exists():
    env_example = Path(__file__).parent.parent / ".env.example"
    assert env_example.exists(), ".env.example должен существовать как шаблон"


def test_env_in_gitignore():
    gitignore = Path(__file__).parent.parent / ".gitignore"
    assert gitignore.exists(), ".gitignore должен существовать"

    content = gitignore.read_text()
    assert (
        ".env" in content
    ), ".env должен быть в .gitignore для предотвращения коммита секретов"
