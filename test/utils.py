"""Collection of utility function to support testing."""

from steamship import File, Tag
from steamship.data import TagKind, TagValueKey


def verify_response(response) -> None:
    """Verify response from the blockifier."""
    assert response.data is not None
    assert response.data.file is not None
    file = response.data.file
    verify_file(file)


def verify_file(file) -> None:
    """Verify the blockified file."""
    assert isinstance(file, (File, File.CreateRequest))
    assert len(file.tags) == 0
    assert file.blocks is not None
    assert len(file.blocks) == 1
    assert file.blocks[0] is not None
    block = file.blocks[0]
    verify_block(block)


def verify_block(block):
    """Verify the block."""

    assert block.text is not None

    assert len(block.tags) > 0
    assert isinstance(block.tags[0], Tag)

    unique_tag_kinds = set()

    for tag in block.tags:
        unique_tag_kinds.add(tag.kind)
        if tag.kind == TagKind.TIMESTAMP:
            assert TagValueKey.START_TIME_S in tag.value
            assert tag.value[TagValueKey.START_TIME_S] is not None
            assert TagValueKey.END_TIME_S in tag.value
            assert tag.value[TagValueKey.END_TIME_S] is not None

    assert TagKind.TOPIC in unique_tag_kinds
    assert TagKind.SUMMARY in unique_tag_kinds
    assert TagKind.TIMESTAMP in unique_tag_kinds
    assert TagKind.TOKENIZATION in unique_tag_kinds
