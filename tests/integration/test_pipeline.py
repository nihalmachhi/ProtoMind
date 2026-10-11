from conftest import write_tinykv_capture

from protomind.capture.pcap_reader import read_capture
from protomind.pipeline import analyze_capture


def test_tinykv_capture_produces_machine_and_spec(tmp_path):
    capture = write_tinykv_capture(tmp_path / "tinykv.pcap")
    streams = read_capture(capture)
    assert {stream.direction for stream in streams} == {"C2S", "S2C"}
    result = analyze_capture(capture, tmp_path / "run")
    assert result["sessions"] == 1
    assert result["framing"]["kind"] == "delimiter"
    assert result["message_count"] == 10
    assert len(result["machine"]["transitions"]) == 5
    assert (tmp_path / "run" / "spec.md").is_file()
    assert (tmp_path / "run" / "machine.mmd").is_file()
