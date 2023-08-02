"""Test assemblyai-s2t-blockifier via integration tests."""
import random
import string
from pathlib import Path
from test import AUDIO_FILES_PATH
from test.utils import verify_file

import pytest
from steamship import File, PluginInstance, Steamship, Task, TaskState
from steamship.base.mime_types import MimeTypes

TRANSCRIBER_HANDLE = "deepgram-transcriber"


def random_name() -> str:
    """Returns a random name suitable for a handle that has low likelihood of colliding with another.

    Output format matches test_[a-z0-9]+, which should be a valid handle.
    """
    letters = string.digits + string.ascii_letters
    return f"test_{''.join(random.choice(letters) for _ in range(10))}".lower()  # noqa: S311


def transcriber_instance(steamship_client: Steamship, punctuate: bool) -> PluginInstance:
    """Instantiate a plugin instance."""
    plugin_instance = steamship_client.use_plugin(
        plugin_handle=TRANSCRIBER_HANDLE,
        config={},
        fetch_if_exists=False,
    )
    assert plugin_instance is not None
    assert plugin_instance.id is not None
    return plugin_instance


@pytest.mark.parametrize("audio_file", AUDIO_FILES_PATH.iterdir())
@pytest.mark.parametrize("punctuate", [False])
def test_blockifier(steamship_client: Steamship, audio_file: Path, punctuate: bool):
    """Test the DeepGram Transcriber via an integration test."""
    file = File.create(
        steamship_client, content=audio_file.open("rb").read(), mime_type=MimeTypes.MP3
    )

    t_instance = transcriber_instance(steamship_client, punctuate)
    blockify_task = file.blockify(plugin_instance=t_instance.handle)
    blockify_task.wait(max_timeout_s=5 * 60, retry_delay_s=1)

    assert isinstance(blockify_task, Task)
    assert blockify_task.state == TaskState.succeeded
    file = blockify_task.output.file

    verify_file(file)
