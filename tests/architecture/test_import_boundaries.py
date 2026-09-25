from pathlib import Path


def test_core_has_no_pgf_or_http_imports():
    root=Path('src/semantik_architect')
    for sub in ('domain','application'):
        for path in (root/sub).rglob('*.py'):
            text=path.read_text(encoding='utf-8')
            assert 'import pgf' not in text, path
            assert 'from http' not in text, path
            assert 'fastapi' not in text.lower(), path


def test_no_language_code_branches_in_core():
    root=Path('src/semantik_architect')
    text='\n'.join(p.read_text(encoding='utf-8') for sub in ('domain','application') for p in (root/sub).rglob('*.py'))
    for code in ('"sq"',"'sq'",'"fr"',"'fr'",'"en"',"'en'"):
        assert f'== {code}' not in text
