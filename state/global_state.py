from typing import TypedDict

from state.certificate_state import CertificateState
from state.conversation_state import ConversationState
from state.evaluation_state import EvaluationState


class GlobalState(TypedDict):
    certificate: CertificateState
    conversation: ConversationState
    evaluation: EvaluationState
