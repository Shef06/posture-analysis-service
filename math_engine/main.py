"""
FastAPI Microservizio: Motore Matematico Puro per Analisi Postura
Calcola Ghost Profile da dati numerici (landmark) senza dipendenze da file video
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os
import numpy as np
from typing import Optional
import uvicorn

# Supporta sia esecuzione diretta che import come package
try:
    # Prova prima import relativi (quando eseguito come package)
    from .models import (
        GhostRequest, GhostProfile, RunAnalysisRequest, RunAnalysisResult,
        VideoExtractionRequest, VideoExtractionResult, RunData
    )
    from .ghost_engine import GhostEngine
except ImportError:
    # Se fallisce, aggiungi il path e usa import assoluti
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from math_engine.models import (
        GhostRequest, GhostProfile, RunAnalysisRequest, RunAnalysisResult,
        VideoExtractionRequest, VideoExtractionResult, RunData
    )
    from math_engine.ghost_engine import GhostEngine

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MATH_ENGINE_API')

# Inizializza FastAPI
app = FastAPI(
    title="Posture Analysis Math Engine",
    description="Microservizio matematico puro per calcolo Ghost Profile e analisi postura",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione, specifica gli origini
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inizializza GhostEngine
ghost_engine = GhostEngine()


@app.get("/")
async def root():
    """Endpoint root per health check"""
    return {
        "service": "Posture Analysis Math Engine",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "compute_ghost_profile": "/v1/compute-ghost-profile",
            "analyze_run": "/v1/analyze-run",
            "extract_from_video": "/v1/extract-from-video"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint - returns 204 No Content"""
    from fastapi.responses import Response
    return Response(status_code=204)


@app.get("/v1/compute-ghost-profile")
async def compute_ghost_profile_info():
    """
    Documentazione endpoint per calcolo Ghost Profile
    Questo endpoint richiede una richiesta POST con body JSON
    """
    return {
        "endpoint": "/v1/compute-ghost-profile",
        "method": "POST",
        "description": "Calcola il Ghost Profile da 5 corse baseline",
        "request_body": {
            "runs": [
                {
                    "frames": [
                        {
                            "landmarks": [
                                {"x": 0.0, "y": 0.0, "z": 0.0, "visibility": 1.0}
                            ] * 33
                        }
                    ]
                }
            ] * 5,
            "target_frames": 100
        },
        "response": {
            "ghost_data": "Lista di 33 landmark medi",
            "tolerances": "Lista di 33 tolleranze (deviazioni standard)",
            "best_run_index": "Indice (0-4) della corsa più vicina alla media",
            "best_run_distance": "Distanza euclidea della best run",
            "normalized_frame_count": "Numero di frame dopo normalizzazione",
            "original_frame_counts": "Numero frame originali per ogni corsa"
        },
        "example_curl": "curl -X POST http://localhost:8000/v1/compute-ghost-profile -H 'Content-Type: application/json' -d '{\"runs\": [...], \"target_frames\": 100}'"
    }


@app.post("/v1/compute-ghost-profile", response_model=GhostProfile)
async def compute_ghost_profile(request: GhostRequest):
    """
    Calcola il Ghost Profile da 5 corse baseline
    
    Logica Matematica:
    1. Allinea temporalmente le 5 corse (interpolazione lineare)
    2. Calcola media punto per punto (X, Y, Z, visibility) per creare lo "Scheletro Ghost"
    3. Calcola le tolleranze (deviazione standard)
    4. Selezione Best Run: confronta matematicamente (Distanza Euclidea) ogni run originale
       con la media calcolata. Trova l'indice (0-4) della run che si avvicina di più.
    
    Args:
        request: GhostRequest con 5 corse baseline
    
    Returns:
        GhostProfile con ghost_data, tolerances, best_run_index
    """
    try:
        logger.info("=== Calcolo Ghost Profile ===")
        logger.info(f"Numero corse: {len(request.runs)}")
        logger.info(f"Frame target: {request.target_frames}")
        
        # Converti RunData in formato numpy
        runs_numpy = []
        original_frame_counts = []
        
        for i, run_data in enumerate(request.runs):
            numpy_run = ghost_engine.convert_to_numpy(run_data)
            runs_numpy.append(numpy_run)
            original_frame_counts.append(len(run_data.frames))
            logger.info(f"  Run {i}: {len(run_data.frames)} frame")
        
        # Calcola Ghost Profile
        ghost_data, tolerances, best_run_index, best_run_distance = ghost_engine.compute_ghost_profile(
            runs_numpy,
            target_frames=request.target_frames
        )
        
        # Converti in formato Pydantic
        ghost_landmarks, tolerance_objects = ghost_engine.convert_from_numpy(ghost_data, tolerances)
        
        normalized_frame_count = len(ghost_data)
        
        logger.info(f"✅ Ghost Profile calcolato: {normalized_frame_count} frame normalizzati")
        logger.info(f"🏆 Best Run: indice {best_run_index}, distanza = {best_run_distance:.6f}")
        
        return GhostProfile(
            ghost_data=ghost_landmarks,
            tolerances=tolerance_objects,
            best_run_index=best_run_index,
            best_run_distance=float(best_run_distance),
            normalized_frame_count=normalized_frame_count,
            original_frame_counts=original_frame_counts
        )
        
    except ValueError as e:
        logger.error(f"❌ Errore validazione: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Errore nel calcolo Ghost Profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")


@app.post("/v1/analyze-run", response_model=RunAnalysisResult)
async def analyze_run(request: RunAnalysisRequest):
    """
    Analizza una nuova corsa confrontandola con il Ghost Profile
    
    Calcola gli scostamenti e ritorna il punteggio/errori.
    
    Args:
        request: RunAnalysisRequest con nuova corsa e Ghost Profile
    
    Returns:
        RunAnalysisResult con errori calcolati
    """
    try:
        logger.info("=== Analisi Corsa ===")
        
        # Converti RunData in formato numpy
        run_numpy = ghost_engine.convert_to_numpy(request.run_data)
        
        # Converti GhostProfile in formato numpy
        # Il GhostProfile contiene landmark medi (33), dobbiamo ricostruire l'array completo
        # Per semplicità, assumiamo che il ghost sia rappresentato da un singolo frame medio
        # In realtà dovremmo avere tutti i frame, ma per ora semplifichiamo
        
        # Ricostruisci ghost_data e tolerances dagli oggetti Pydantic
        num_frames = request.ghost_profile.normalized_frame_count
        ghost_data = np.zeros((num_frames, 33, 4), dtype=np.float32)
        tolerances = np.zeros((num_frames, 33, 4), dtype=np.float32)
        
        # Ripeti i landmark medi per tutti i frame (semplificazione)
        for i, landmark in enumerate(request.ghost_profile.ghost_data):
            ghost_data[:, i, 0] = landmark.x
            ghost_data[:, i, 1] = landmark.y
            ghost_data[:, i, 2] = landmark.z
            ghost_data[:, i, 3] = landmark.visibility
        
        for i, tolerance in enumerate(request.ghost_profile.tolerances):
            tolerances[:, i, 0] = tolerance.x
            tolerances[:, i, 1] = tolerance.y
            tolerances[:, i, 2] = tolerance.z
            tolerances[:, i, 3] = tolerance.visibility
        
        # Analizza la corsa
        total_error, mean_error, max_error, frame_errors = ghost_engine.analyze_run(
            run_numpy, ghost_data, tolerances
        )
        
        logger.info(f"✅ Analisi completata: errore totale = {total_error:.6f}")
        
        return RunAnalysisResult(
            total_error=total_error,
            mean_error=mean_error,
            max_error=max_error,
            frame_errors=frame_errors,
            normalized_frame_count=len(frame_errors)
        )
        
    except ValueError as e:
        logger.error(f"❌ Errore validazione: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Errore nell'analisi: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")


@app.post("/v1/extract-from-video", response_model=VideoExtractionResult)
async def extract_from_video(
    video: UploadFile = File(...),
    view_type: str = "posterior",
    model_complexity: int = 1,
    min_detection_confidence: float = 0.5
):
    """
    Estrae landmark da un video usando MediaPipe
    
    Utility opzionale per estrarre dati "al volo" da un video.
    La logica del ghost deve rimanere separata dai file.
    
    Args:
        video: File video caricato
        view_type: Tipo di vista ('posterior' o 'lateral')
        model_complexity: Complessità modello MediaPipe (0-2)
        min_detection_confidence: Soglia rilevamento (0-1)
    
    Returns:
        VideoExtractionResult con RunData estratto
    """
    try:
        import cv2
        import mediapipe as mp
        import tempfile
        import os
        
        logger.info("=== Estrazione Landmark da Video ===")
        logger.info(f"File: {video.filename}")
        logger.info(f"View type: {view_type}, Model complexity: {model_complexity}")
        
        # Salva file temporaneo
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_path = tmp_file.name
            content = await video.read()
            tmp_file.write(content)
        
        try:
            # Apri video
            cap = cv2.VideoCapture(tmp_path)
            if not cap.isOpened():
                raise ValueError(f"Impossibile aprire il video: {tmp_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Inizializza MediaPipe
            mp_pose = mp.solutions.pose
            pose = mp_pose.Pose(
                model_complexity=model_complexity,
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=0.1,
                enable_segmentation=False,
                smooth_landmarks=False
            )
            
            # Estrai landmark frame per frame
            frames_data = []
            frames_with_pose = 0
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Converti BGR a RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Processa con MediaPipe
                results = pose.process(frame_rgb)
                
                if results.pose_world_landmarks:
                    # Estrai landmark
                    landmarks = []
                    for landmark in results.pose_world_landmarks.landmark:
                        landmarks.append({
                            'x': landmark.x,
                            'y': landmark.y,
                            'z': landmark.z,
                            'visibility': landmark.visibility
                        })
                    
                    # Crea FrameData
                    try:
                        from .models import FrameData, Landmark
                    except ImportError:
                        from math_engine.models import FrameData, Landmark
                    frame_data = FrameData(
                        landmarks=[Landmark(**lm) for lm in landmarks]
                    )
                    frames_data.append(frame_data)
                    frames_with_pose += 1
                else:
                    # Frame senza pose: crea landmark vuoti (tutti zero)
                    try:
                        from .models import FrameData, Landmark
                    except ImportError:
                        from math_engine.models import FrameData, Landmark
                    empty_landmarks = [Landmark(x=0.0, y=0.0, z=0.0, visibility=0.0) for _ in range(33)]
                    frame_data = FrameData(landmarks=empty_landmarks)
                    frames_data.append(frame_data)
                
                frame_count += 1
            
            cap.release()
            pose.close()
            
            # Crea RunData
            run_data = RunData(frames=frames_data)
            
            success_rate = (frames_with_pose / frame_count * 100.0) if frame_count > 0 else 0.0
            
            logger.info(f"✅ Estrazione completata: {frames_with_pose}/{frame_count} frame con pose ({success_rate:.1f}%)")
            
            return VideoExtractionResult(
                run_data=run_data,
                fps=float(fps),
                total_frames=frame_count,
                frames_with_pose=frames_with_pose,
                success_rate=success_rate
            )
            
        finally:
            # Pulisci file temporaneo
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
    except HTTPException:
        # Rilancia HTTPException già gestite (MediaPipe non disponibile)
        raise
    except ImportError as e:
        logger.error(f"❌ Dipendenze mancanti: {e}")
        raise HTTPException(
            status_code=503,
            detail=(
                "MediaPipe o OpenCV non disponibili. "
                "Installa con: pip install mediapipe opencv-python-headless "
                "(richiede Python 3.12)"
            )
        )
    except Exception as e:
        logger.error(f"❌ Errore nell'estrazione: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")


if __name__ == "__main__":
    # Esegui come modulo per supportare import relativi
    uvicorn.run("math_engine.main:app", host="0.0.0.0", port=8000, reload=True)

