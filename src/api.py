"""DeepgramAI transcriber.

An audio file is loaded and converted into blocks, with tags added according to the plugin configuration.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type
from uuid import uuid4

from deepgram import Deepgram
from steamship import Steamship, SteamshipError, Tag
from steamship.data.workspace import SignedUrl
from steamship.invocable import Config
from steamship.plugin.blockifier import Transcriber
from steamship.utils.signed_urls import upload_to_signed_url

from config import DeepgramAITranscriberConfig
from parsers import (
    get_transcript,
    parse_paragraphs,
    parse_summaries,
    parse_timestamps,
    parse_topics,
)


def upload_audio_file(client: Steamship, data: bytes) -> str:
    unique_file_id = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{uuid4()}"
    current_workspace = client.get_workspace()

    writing_signed_url = current_workspace.create_signed_url(
        SignedUrl.Request(
            bucket=SignedUrl.Bucket.PLUGIN_DATA,
            filepath=unique_file_id,
            operation=SignedUrl.Operation.WRITE,
        )
    ).signed_url
    upload_to_signed_url(writing_signed_url, data)

    return current_workspace.create_signed_url(
        SignedUrl.Request(
            bucket=SignedUrl.Bucket.PLUGIN_DATA,
            filepath=unique_file_id,
            operation=SignedUrl.Operation.READ,
        )
    ).signed_url


class DeepgramAITranscriber(Transcriber):
    """Transcribe audio files.

    Attributes
    ----------
    config : DeepgramAITranscriberConfig
        The required configuration used to instantiate a deepgram-transcriber
    """

    config: DeepgramAITranscriberConfig
    _transcription_result = None

    BASE_URL = "https://api.deepgram.com/v1"
    BASE_HEADERS = {
        "content-type": "application/json",
    }

    def config_cls(self) -> Type[Config]:
        """Return the Configuration class."""
        return DeepgramAITranscriberConfig

    def start_transcription(self, audio_file: bytes) -> str:
        logging.info("DeepGram Transcriber received run request.")
        signed_url = upload_audio_file(client=self.client, data=audio_file)

        transcription_response = self._transcribe_with_deepgram(file_uri=signed_url)
        try:
            self._transcription_result = transcription_response["results"]["channels"][0][
                "alternatives"
            ][0]
            return transcription_response.get("metadata", {}).get("request_id", "000")
        except KeyError:
            raise SteamshipError("Transcription unsuccessful")

    def get_transcript(self, transcript_id: str) -> (Optional[str], Optional[List[Tag]]):
        return self._process_transcription_result(self._transcription_result)

    def _transcribe_with_deepgram(self, file_uri: str) -> Dict[str, Any]:
        """Start to transcribe the audio file stored on s3 and return the JSON response."""
        return Deepgram(self.config.deepgram_api_token).transcription.sync_prerecorded(
            source={"url": file_uri},
            options={
                "utterances": self.config.utterances,
                "utt_split": self.config.utt_split,
                "detect_entities": self.config.detect_entities,
                "summarize": self.config.summarize,
                "paragraphs": self.config.paragraphs,
                "detect_language": self.config.detect_language,
                "detect_topics": self.config.detect_topics,
                "translation": self.config.translation,
                "analyze_sentiment": self.config.analyze_sentiment,
                "sent_thresh": self.config.sent_thresh,
                "model": self.config.model,
                "version": self.config.version,
                "language": self.config.language,
                "punctuate": self.config.punctuate,
                "profanity_filter": self.config.profanity_filter,
                "redact": self.config.redact,
                "diarize": self.config.diarize,
                "diarize_version": self.config.diarize_version,
                "multichannel": self.config.multichannel,
                "alternatives": self.config.alternatives,
                "numbers": self.config.numbers,
                "numbers_spaces": self.config.numbers_spaces,
                "search": self.config.search,
                "keywords": self.config.keywords,
                "ner": self.config.ner,
                "tier": self.config.tier,
                "dates": self.config.dates,
                "date_format": self.config.date_format,
                "times": self.config.times,
                "dictation": self.config.dictation,
                "measurements": self.config.measurements,
                "replace": self.config.replace,
            },
        )

    def _process_transcription_result(
            self, transcription_result: Dict[str, Any]
    ) -> (str, Optional[List[Tag]]):
        transcription = get_transcript(transcription_result)

        timestamp_tags, word_idx_to_char_idx = parse_timestamps(transcription_result)

        tags = [
            *timestamp_tags,
            *parse_summaries(transcription_result, word_idx_to_char_idx),
            *parse_topics(transcription_result, word_idx_to_char_idx),
            *parse_paragraphs(transcription_result, word_idx_to_char_idx),
        ]
        return transcription, tags
