"""Test assemblyai-s2t-blockifier via unit tests."""
from pathlib import Path

import pytest as pytest
from steamship import Steamship
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.request import PluginRequest

from src.api import DeepgramAITranscriber
from test import AUDIO_FILES_PATH
from test.conftest import config
from test.utils import verify_response


@pytest.mark.parametrize("audio_file", AUDIO_FILES_PATH.iterdir())
@pytest.mark.parametrize("punctuate", [False])
def test_transcriber(steamship_client: Steamship, audio_file: Path, punctuate: bool) -> None:
    """Test DeepgramAI (S2T) Transcriber without edge cases."""
    client = Steamship()

    transcriber = DeepgramAITranscriber(client=client, config=config(punctuate))

    request = PluginRequest(
        data=RawDataPluginInput(data=audio_file.open("rb").read())
    )
    response = transcriber.run(request)

    verify_response(response)
