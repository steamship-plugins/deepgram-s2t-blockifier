from typing import List, Optional

from steamship.invocable import Config


class DeepgramAITranscriberConfig(Config):
    """Config object containing required configuration parameters to initialize a DeepgramAIBlockifier.

    References for the different meanings and values of these properties can be found in the Deepgram docs:
    https://developers.deepgram.com/api-reference/speech-recognition-api#operation/transcribeAudio
    """

    deepgram_api_token: str

    tier: Optional[str] = "base"
    model: Optional[str] = "general"
    version: Optional[str] = "latest"
    language: Optional[str] = None
    detect_language: Optional[bool] = None
    punctuate: Optional[bool] = None
    profanity_filter: Optional[bool] = None
    redact: Optional[List[str]] = None
    diarize: Optional[bool] = None
    diarize_version: Optional[str] = None
    smart_format: Optional[bool] = False
    multichannel: Optional[bool] = None
    alternatives: Optional[int] = 1

    search: Optional[List[str]] = None
    replace: Optional[str] = None
    keywords: Optional[List[str]] = None
    paragraphs: Optional[bool] = None
    summarize: Optional[bool] = None
    detect_topics: Optional[bool] = None
    utterances: Optional[bool] = None
    utt_split: Optional[float] = None

    # Not documented
    analyze_sentiment: Optional[bool] = None
    date_format: Optional[str] = None
    dates: Optional[bool] = None
    detect_entities: Optional[bool] = None
    dictation: Optional[bool] = None
    measurements: Optional[bool] = None
    ner: Optional[str] = None
    numbers: Optional[bool] = None
    numbers_spaces: Optional[bool] = None
    sent_thresh: Optional[float] = None
    times: Optional[bool] = None
    translation: Optional[List[str]] = None
