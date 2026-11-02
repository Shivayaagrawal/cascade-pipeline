"""Empty bundles stop before any existing processor."""

from cascadeguard.pipeline import run_b0, run_b1, run_b2
from cascadeguard_facade.adapters import b0_prefix, b2_lexical_v3
from cascadeguard_facade.contracts import CandidateBundle
from cascadeguard_facade.router import route


def _empty() -> CandidateBundle:
    return CandidateBundle("utt-000", (), "v1_injector", "SYNTHETIC_PROXY")


def test_router_empty_bundle_does_not_call_run_b0(monkeypatch) -> None:
    def fail(*_args, **_kwargs):
        raise AssertionError("run_b0 was called")

    monkeypatch.setattr("cascadeguard_facade.adapters.b0_prefix.run_b0", fail)
    monkeypatch.setattr("cascadeguard.pipeline.run_b0", fail)
    record = route("b0_prefix", _empty())
    assert record.raw.invoked is False
    assert record.normalized.action == "HOLD"
    assert record.normalized.reason == "EMPTY_BUNDLE"
    assert record.normalized.committed_frame is None


def test_adapter_empty_bundle_does_not_call_lexical_recovery(monkeypatch) -> None:
    def fail(*_args, **_kwargs):
        raise AssertionError("recovery_action was called")

    monkeypatch.setattr(
        "cascadeguard_facade.adapters.b2_lexical_v3.recovery_action",
        fail,
    )
    raw, normalized = b2_lexical_v3.execute(_empty(), {})
    assert raw.invoked is False
    assert normalized.reason == "EMPTY_BUNDLE"


def test_router_empty_does_not_import_a_processor_call(monkeypatch) -> None:
    def fail(*_args, **_kwargs):
        raise AssertionError("forced_selection was called")

    monkeypatch.setattr(
        "cascadeguard_facade.adapters.b1_forced_lexical.forced_selection",
        fail,
    )
    record = route("b1_forced_lexical", _empty())
    assert record.normalized.reason == "EMPTY_BUNDLE"
    assert record.raw.invoked is False


def test_existing_runners_still_exist() -> None:
    assert callable(run_b0)
    assert callable(run_b1)
    assert callable(run_b2)
    assert callable(b0_prefix.execute)
