from pathlib import Path

from semantik_architect.adapters.runtime.filesystem import FilesystemRuntimeCatalog

from tests.integration.test_full_pipeline_fake_pgf import _make_runtime


def test_runtime_hash_tampering_is_detected(tmp_path: Path):
    _make_runtime(tmp_path)
    (tmp_path/'r1'/'lexicon.json').write_text('{"tampered":true}',encoding='utf-8')
    catalog=FilesystemRuntimeCatalog(tmp_path,sa_version='1.0.0')
    report=catalog.validate('rt1')
    assert report['valid'] is False
    assert any(error.startswith('sha256:lex-en') for error in report['errors'])
