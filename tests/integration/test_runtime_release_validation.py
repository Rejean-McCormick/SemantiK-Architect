from pathlib import Path

from semantik_architect.adapters.realization.gf import GfBridgeRealizer
from semantik_architect.bootstrap import build_container

from .test_full_pipeline_fake_pgf import FakePgfRuntime, _make_runtime


def test_runtime_release_validator_accepts_complete_fixture(tmp_path: Path):
    _make_runtime(tmp_path)
    container=build_container(tmp_path,realizer=GfBridgeRealizer(runtime_factory=FakePgfRuntime))
    report=container.validate_runtime.execute('rt1')
    assert report['valid'] is True, report
