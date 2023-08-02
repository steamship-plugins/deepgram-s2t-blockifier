"""Parsers to extract tags from DeepGram's responses."""
from typing import Any, Dict, List, Literal, Union

from deepgram._types import PrerecordedTranscriptionResponse
from steamship import Tag
from steamship.data.tags.tag import SummaryTag, TimestampTag, TokenizationTag, TopicTag

TranscriptionResult = Dict[str, Any]
WordIdxToCharIdx = List[Dict[Union[Literal["start"], Literal["end"]], int]]


def get_transcript(transcription_result: TranscriptionResult) -> str:
    return transcription_result.get("transcript", "")


def parse_timestamps(transcription_result: TranscriptionResult) -> (List[Tag], WordIdxToCharIdx):
    """Extract timestamp tags from transcription response."""
    word_idx_to_char_idx = []
    tags = []
    char_idx = 0
    for word in transcription_result["words"]:
        word_length = len(word["punctuated_word"])
        tags.append(
            TimestampTag(
                start_time_s=word["start"],
                end_time_s=word["end"],
                start_idx=char_idx,
                end_idx=char_idx + word_length,
            )
        )
        word_idx_to_char_idx.append({"start": char_idx, "end": char_idx + word_length})
        char_idx += word_length + 1
    return tags, word_idx_to_char_idx


def parse_paragraphs(
    transcription_result: PrerecordedTranscriptionResponse, word_idx_to_char_idx: WordIdxToCharIdx
) -> List[Tag]:
    tags = []
    word_idx = 0
    if "paragraphs" in transcription_result:
        for paragraph in transcription_result.get("paragraphs", {}).get("paragraphs", []):
            tags.append(
                TokenizationTag(
                    type=TokenizationTag.Type.PARAGRAPH,
                    start_idx=word_idx_to_char_idx[word_idx]["start"],
                    end_idx=word_idx_to_char_idx[word_idx + paragraph["num_words"]]["end"],
                )
            )
            sentence_idx = 0
            for sentence in paragraph.get("sentences", []):
                sentence_word_length = len(sentence["text"].split())
                tags.append(
                    TokenizationTag(
                        type=TokenizationTag.Type.SENTENCE,
                        start_idx=word_idx_to_char_idx[word_idx + sentence_idx]["start"],
                        end_idx=word_idx_to_char_idx[
                            word_idx + sentence_idx + sentence_word_length - 1
                        ]["end"],
                    )
                )
                sentence_idx += sentence_word_length

    return tags


def parse_summaries(
    transcription_result: PrerecordedTranscriptionResponse, word_idx_to_char_idx: WordIdxToCharIdx
) -> List[Tag]:
    """Extract summary from transcription response."""
    tags = []
    if "summaries" in transcription_result:
        for summary in transcription_result.get("summaries", []):
            tags.append(
                SummaryTag(
                    summary=summary["summary"],
                    end_idx=word_idx_to_char_idx[summary["start_word"]]["start"],
                    start_idx=word_idx_to_char_idx[summary["end_word"] - 1]["end"],
                )
            )

    return tags


def parse_topics(
    transcription_result: PrerecordedTranscriptionResponse, word_idx_to_char_idx
) -> List[Tag]:
    tags = []
    if "topics" in transcription_result:
        for topic in transcription_result.get("topics", []):
            if "topics" in topic and topic["topics"]:
                for topic_tag in topic["topics"]:
                    tags.append(
                        TopicTag(
                            topic=topic_tag,
                            end_idx=word_idx_to_char_idx[topic["start_word"]],
                            start_idx=word_idx_to_char_idx[topic["end_word"]],
                        )
                    )
            else:
                tags.append(
                    TopicTag(
                        topic="UNKNOWN",
                        end_idx=word_idx_to_char_idx[topic["start_word"]]["start"],
                        start_idx=word_idx_to_char_idx[topic["end_word"] - 1]["end"],
                    )
                )
    return tags
