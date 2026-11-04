from protomind.evaluation import evaluate, framing_fixtures


def test_synthetic_evaluation_is_deterministic_and_fully_passing():
    first = evaluate()
    second = evaluate()
    assert first == second
    assert first["kind"] == "synthetic"
    assert first["scenarios"] == 5
    assert first["metrics"]["pass_rate"] == 1.0
    assert first["metrics"]["framing_accuracy"] == 1.0
    assert first["redaction"]["passed"] is True
    assert first["boundary_case"]["scenario"] == "opaque_binary"


def test_framing_fixtures_match_the_python_segmenter():
    fixtures = {item["name"]: item for item in framing_fixtures()}
    assert set(fixtures) == {"tinykv_delimiter", "length_prefix", "fixed_size", "opaque_binary"}
    assert fixtures["tinykv_delimiter"]["expected"]["kind"] == "delimiter"
    assert fixtures["length_prefix"]["expected"]["kind"] == "length_prefix"
    assert fixtures["fixed_size"]["expected"]["kind"] == "fixed_size"
    assert fixtures["opaque_binary"]["expected"]["kind"] == "whole_stream"
    assert all(item["streams_hex"] for item in fixtures.values())
