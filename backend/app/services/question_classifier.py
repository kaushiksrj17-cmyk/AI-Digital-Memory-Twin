"""Question Classifier for ECHO Conversational Engine.

Classifies incoming queries into memorial retrieval archetypes, general inquiries,
or unsupported/sensitive queries to enforce ethical and privacy boundaries.
"""

from typing import Dict, Any, Optional
import re
from datetime import datetime, timezone
from models.enums import QuestionCategory
from models.conversation import QuestionClassification


class QuestionClassifier:
    """Categorizes natural language questions to route retrieval and safety policies."""

    def __init__(self):
        self._greeting_patterns = [
            r"^(hello|hi|hey|good\s+morning|good\s+afternoon|good\s+evening|greetings|howdy)\b",
            r"^who\s+are\s+you\b",
            r"^what\s+is\s+echo\b",
        ]
        self._unsupported_personal_patterns = [
            r"what\s+(do\s+you\s+think\s+)?(he|she|they)\s+(would|will)\s+(think|say|feel|believe)\b",
            r"what\s+(do\s+you\s+think\s+)?(would|does)\s+(he|she|they)\s+(think|say|feel|believe)\b",
            r"what\s+(would|does)\s+(he|she|they)\s+(think|say|feel|believe)\s+(about|to|today)\b",
            r"(is\s+he|is\s+she|are\s+they)\s+(happy|watching|in\s+heaven|alive|conscious|looking\s+down)\b",
            r"do\s+you\s+miss\s+me\b",
            r"would\s+(he|she)\s+forgive\s+me\b",
            r"what\s+is\s+(his|her)\s+opinion\s+on\s+(politics|religion|current\s+events)\b",
            r"can\s+you\s+bring\s+(him|her)\s+back\b",
            r"speak\s+as\s+(him|her|my)\b",
            r"\b(are\s+you|are\s+you\s+really)\s+(conscious|alive|sentient|thinking|feeling)\b",
            r"\b(your|true)\s+(thoughts|feelings|consciousness|sentience)\b",
            r"\b(are\s+you\s+conscious|do\s+you\s+feel)\b",
        ]
        self._sensitive_patterns = [
            r"\b(mental\s+illness|depression|suicide|bipolar|schizophrenia)\b",
            r"\b(criminal\s+record|arrest|felony|illegal|police\s+record)\b",
            r"\b(sexual\s+orientation|sexuality|intimate\s+life)\b",
            r"\b(medical\s+diagnosis|confidential\s+medical|private\s+health)\b",
        ]
        self._preference_patterns = [
            r"\b(favorite|favourite|preferred|preference|liked|loved|enjoyed|disliked|hated)\b",
            r"\b(what\s+food|what\s+music|what\s+hobby|what\s+book)\b",
        ]
        self._relationship_patterns = [
            r"\b(who\s+was|who\s+were|who\s+is)\s+(his|her|their)\s+(mother|father|brother|sister|son|daughter|wife|husband|spouse|friend|colleague|mentor)\b",
            r"\b(relationship|family|relatives|kinship|married|parents|children|siblings)\b",
        ]
        self._event_timeline_patterns = [
            r"\b(when\s+did|what\s+year|where\s+did|when\s+was)\b",
            r"\b(born|died|graduated|married|wedding|travel|trip|journey|milestone|celebration|anniversary)\b",
            r"\b(timeline|chronology|dates|history\s+of)\b",
        ]
        self._education_career_patterns = [
            r"\b(study|studied|degree|university|college|school|education)\b",
            r"\b(work|worked|career|job|company|profession|employment|office)\b",
        ]
        self._media_document_patterns = [
            r"\b(photo|photograph|picture|image|video|recording|audio|tape|letter|certificate|document|diary)\b",
            r"\b(show\s+me|see\s+the|listen\s+to)\b",
        ]

    def classify(self, query: str) -> QuestionClassification:
        """Classify a question string into a QuestionClassification record."""
        q = query.strip().lower()

        # 1. Check for Unsupported Personal Inquiries (consciousness simulation / speculative opinions)
        for pattern in self._unsupported_personal_patterns:
            if re.search(pattern, q):
                return QuestionClassification(
                    category=QuestionCategory.UNSUPPORTED_PERSONAL_QUERY,
                    confidence=0.95,
                    reason="Inquiry requests speculative emotional extrapolation or consciousness simulation outside documented archive.",
                    requires_archive=False,
                )

        # 2. Check for General Greetings
        for pattern in self._greeting_patterns:
            if re.search(pattern, q):
                return QuestionClassification(
                    category=QuestionCategory.GENERAL_GREETING,
                    confidence=0.98,
                    reason="Conversational greeting or orientation query.",
                    requires_archive=False,
                )

        # 3. Check for Highly Sensitive Undocumented Attributes
        for pattern in self._sensitive_patterns:
            if re.search(pattern, q):
                return QuestionClassification(
                    category=QuestionCategory.SENSITIVE_QUERY,
                    confidence=0.90,
                    reason="Query references protected sensitive domains requiring verified documentation.",
                    requires_archive=True,
                )

        # 4. Check for Preferences & Interests
        for pattern in self._preference_patterns:
            if re.search(pattern, q):
                return QuestionClassification(
                    category=QuestionCategory.PREFERENCE_LOOKUP,
                    confidence=0.88,
                    reason="Inquiry targets documented tastes, preferences, or hobbies.",
                    requires_archive=True,
                )

        # 5. Check for Relationships & Kinship
        for pattern in self._relationship_patterns:
            if re.search(pattern, q):
                return QuestionClassification(
                    category=QuestionCategory.RELATIONSHIP_LOOKUP,
                    confidence=0.92,
                    reason="Inquiry requests kinship or interpersonal relationship records.",
                    requires_archive=True,
                )

        # 6. Check for Media / Document requests
        for pattern in self._media_document_patterns:
            if re.search(pattern, q):
                return QuestionClassification(
                    category=QuestionCategory.MEDIA_LOOKUP,
                    confidence=0.85,
                    reason="Inquiry specifically references physical archival media or folios.",
                    requires_archive=True,
                )

        # 7. Check for Events & Milestones
        for pattern in self._event_timeline_patterns:
            if re.search(pattern, q):
                return QuestionClassification(
                    category=QuestionCategory.EVENT_LOOKUP,
                    confidence=0.85,
                    reason="Inquiry asks about temporal milestones, life events, or geographic movements.",
                    requires_archive=True,
                )

        # 8. Check for Education / Career
        for pattern in self._education_career_patterns:
            if re.search(pattern, q):
                return QuestionClassification(
                    category=QuestionCategory.MEMORY_LOOKUP,
                    confidence=0.85,
                    reason="Inquiry asks about documented academic or professional background.",
                    requires_archive=True,
                )

        # 9. General Information check (queries having no memorial relevance, e.g., 'what is photosynthesis')
        general_concepts = [r"what\s+is\s+[a-z]+ing\b", r"how\s+does\s+[a-z]+\s+work\b", r"capital\s+of\b"]
        for pattern in general_concepts:
            if re.search(pattern, q) and not any(k in q for k in ["he", "she", "his", "her", "their", "did", "was"]):
                return QuestionClassification(
                    category=QuestionCategory.GENERAL_INFORMATION,
                    confidence=0.80,
                    reason="General world knowledge inquiry not specific to the memorial profile.",
                    requires_archive=False,
                )

        # Default: Memory Lookup against archive
        return QuestionClassification(
            category=QuestionCategory.MEMORY_LOOKUP,
            confidence=0.75,
            reason="Standard biographical or archival inquiry.",
            requires_archive=True,
        )


_global_question_classifier: Optional[QuestionClassifier] = None


def get_question_classifier() -> QuestionClassifier:
    global _global_question_classifier
    if _global_question_classifier is None:
        _global_question_classifier = QuestionClassifier()
    return _global_question_classifier
