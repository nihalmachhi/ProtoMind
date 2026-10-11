from protomind.segmentation.segmenters import (
    infer_framing,
    length_prefix_candidate,
    split_delimited,
)


def test_delimiter_segments_concatenated_commands():
    stream = b"HELLO x\r\nAUTH y z\r\nQUIT\r\n"
    assert split_delimited(stream, b"\r\n") == [b"HELLO x\r\n", b"AUTH y z\r\n", b"QUIT\r\n"]
    result = infer_framing([stream])
    assert result.kind == "delimiter"
    assert len(result.messages) == 3


def test_length_prefix_finds_big_endian_payload_lengths():
    stream = b"\x00\x03abc\x00\x02de"
    result = length_prefix_candidate([stream], threshold=0.8)
    assert result is not None
    assert result.params["width"] == 2
    assert len(result.messages) == 2
