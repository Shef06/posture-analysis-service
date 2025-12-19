"""
Modelli Pydantic per il Motore Matematico di Analisi Postura
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum


class Landmark(BaseModel):
    """Singolo landmark MediaPipe (33 landmark per frame)"""
    x: float = Field(..., description="Coordinate X normalizzata (0-1)")
    y: float = Field(..., description="Coordinate Y normalizzata (0-1)")
    z: float = Field(..., description="Coordinate Z normalizzata (profondità)")
    visibility: float = Field(default=1.0, ge=0.0, le=1.0, description="Visibilità del landmark (0-1)")

    @field_validator('x', 'y', 'z')
    @classmethod
    def validate_coordinates(cls, v):
        """Valida che le coordinate siano numeri finiti"""
        if not isinstance(v, (int, float)):
            raise ValueError("Coordinate devono essere numeri")
        if not (-10.0 <= v <= 10.0):  # MediaPipe world coordinates possono essere fuori 0-1
            raise ValueError(f"Coordinate fuori range valido: {v}")
        return float(v)


class FrameData(BaseModel):
    """Dati di un singolo frame (33 landmark)"""
    landmarks: List[Landmark] = Field(..., min_length=33, max_length=33, description="Lista di 33 landmark MediaPipe")

    @field_validator('landmarks')
    @classmethod
    def validate_landmarks_count(cls, v):
        """Verifica che ci siano esattamente 33 landmark"""
        if len(v) != 33:
            raise ValueError(f"Devono esserci esattamente 33 landmark, trovati {len(v)}")
        return v


class RunData(BaseModel):
    """Dati di una singola corsa (lista di frame)"""
    frames: List[FrameData] = Field(..., min_length=1, description="Lista di frame con landmark")

    @field_validator('frames')
    @classmethod
    def validate_frames(cls, v):
        """Verifica che ci sia almeno un frame"""
        if len(v) == 0:
            raise ValueError("Una corsa deve contenere almeno un frame")
        return v


class GhostRequest(BaseModel):
    """Richiesta per calcolare il profilo Ghost da 5 corse baseline"""
    runs: List[RunData] = Field(..., min_length=5, max_length=5, description="Esattamente 5 corse baseline")
    target_frames: Optional[int] = Field(
        default=None,
        description="Numero target di frame dopo normalizzazione temporale. Se None, usa la media delle lunghezze"
    )

    @field_validator('runs')
    @classmethod
    def validate_runs_count(cls, v):
        """Verifica che ci siano esattamente 5 corse"""
        if len(v) != 5:
            raise ValueError(f"Devono esserci esattamente 5 corse, trovate {len(v)}")
        return v


class Tolerance(BaseModel):
    """Tolleranza (deviazione standard) per un landmark"""
    x: float = Field(..., ge=0.0, description="Deviazione standard X")
    y: float = Field(..., ge=0.0, description="Deviazione standard Y")
    z: float = Field(..., ge=0.0, description="Deviazione standard Z")
    visibility: float = Field(..., ge=0.0, le=1.0, description="Deviazione standard visibilità")


class GhostProfile(BaseModel):
    """Profilo Ghost calcolato (media + tolleranze)"""
    ghost_data: List[Landmark] = Field(..., min_length=33, max_length=33, description="Landmark medi (Ghost)")
    tolerances: List[Tolerance] = Field(..., min_length=33, max_length=33, description="Tolleranze per ogni landmark")
    best_run_index: int = Field(..., ge=0, le=4, description="Indice (0-4) della corsa più vicina alla media")
    best_run_distance: float = Field(..., ge=0.0, description="Distanza euclidea della best run dalla media")
    normalized_frame_count: int = Field(..., ge=1, description="Numero di frame dopo normalizzazione temporale")
    original_frame_counts: List[int] = Field(..., min_length=5, max_length=5, description="Numero frame originali per ogni corsa")


class RunAnalysisRequest(BaseModel):
    """Richiesta per analizzare una nuova corsa rispetto al Ghost Profile"""
    run_data: RunData = Field(..., description="Dati della nuova corsa da analizzare")
    ghost_profile: GhostProfile = Field(..., description="Profilo Ghost di riferimento")


class RunAnalysisResult(BaseModel):
    """Risultato dell'analisi di una corsa"""
    total_error: float = Field(..., ge=0.0, description="Errore totale (somma distanze euclidee)")
    mean_error: float = Field(..., ge=0.0, description="Errore medio per frame")
    max_error: float = Field(..., ge=0.0, description="Errore massimo per frame")
    frame_errors: List[float] = Field(..., description="Errore per ogni frame")
    normalized_frame_count: int = Field(..., ge=1, description="Numero di frame dopo normalizzazione")


class ViewType(str, Enum):
    """Tipo di vista per estrazione video"""
    POSTERIOR = "posterior"
    LATERAL = "lateral"


class VideoExtractionRequest(BaseModel):
    """Richiesta per estrarre landmark da un video"""
    video_path: str = Field(..., description="Percorso del video (solo per validazione, il video viene caricato separatamente)")
    view_type: ViewType = Field(default=ViewType.POSTERIOR, description="Tipo di vista")
    model_complexity: int = Field(default=1, ge=0, le=2, description="Complessità modello MediaPipe (0-2)")
    min_detection_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Soglia rilevamento")


class VideoExtractionResult(BaseModel):
    """Risultato estrazione landmark da video"""
    run_data: RunData = Field(..., description="Dati estratti dal video")
    fps: float = Field(..., ge=0.0, description="FPS del video")
    total_frames: int = Field(..., ge=1, description="Numero totale di frame")
    frames_with_pose: int = Field(..., ge=0, description="Frame con pose rilevata")
    success_rate: float = Field(..., ge=0.0, le=100.0, description="Percentuale successo rilevamento")

