from enum import Enum


class DetectionState(str, Enum):
    STRUCTURE_DETECTED = "structure_detected"
    SOTA_CANDIDATE = "sota_candidate"
    WAITING_FOR_START = "waiting_for_start"
    CABALLO_CONFIRMED = "caballo_confirmed"
    DESCEND_TIMEFRAME = "descend_timeframe"
    CHILD_STRUCTURE_DETECTED = "child_structure_detected"
    CHILD_SOTA = "child_sota"
    CHILD_CABALLO = "child_caballo"
    REY = "rey"
