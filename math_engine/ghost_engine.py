"""
Motore Matematico Puro per calcolo Ghost Profile
Implementa normalizzazione temporale, calcolo media, tolleranze e best run selection
"""
import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger('GHOST_ENGINE')


class GhostEngine:
    """
    Engine matematico per calcolo Ghost Profile da multiple corse
    """
    
    # Numero di landmark MediaPipe
    NUM_LANDMARKS = 33
    
    def __init__(self):
        """Inizializza il GhostEngine"""
        pass
    
    def normalize_temporal(self, runs_data: List[List[np.ndarray]], target_frames: int = None) -> List[List[np.ndarray]]:
        """
        Normalizza temporalmente le corse usando interpolazione lineare
        Tutte le corse vengono allineate allo stesso numero di frame
        
        Args:
            runs_data: Lista di corse, ogni corsa è una lista di array numpy (frame x landmark x 4)
                      Ogni array ha shape (NUM_LANDMARKS, 4) dove 4 = [x, y, z, visibility]
            target_frames: Numero target di frame. Se None, usa la media delle lunghezze
        
        Returns:
            Lista di corse normalizzate temporalmente (stesso numero di frame)
        """
        if not runs_data:
            raise ValueError("Lista corse vuota")
        
        # Calcola numero target di frame
        if target_frames is None:
            frame_counts = [len(run) for run in runs_data]
            target_frames = int(np.mean(frame_counts))
            logger.info(f"📊 Numero frame target (media): {target_frames}")
        else:
            logger.info(f"📊 Numero frame target (specificato): {target_frames}")
        
        normalized_runs = []
        
        for i, run in enumerate(runs_data):
            original_frames = len(run)
            
            if original_frames == target_frames:
                # Già della lunghezza corretta
                normalized_runs.append(run)
                logger.debug(f"  Run {i}: {original_frames} frame (già corretto)")
                continue
            
            # Interpolazione lineare
            normalized_run = self._interpolate_run(run, target_frames)
            normalized_runs.append(normalized_run)
            logger.debug(f"  Run {i}: {original_frames} → {target_frames} frame")
        
        return normalized_runs
    
    def _interpolate_run(self, run: List[np.ndarray], target_frames: int) -> List[np.ndarray]:
        """
        Interpola una singola corsa a target_frames frame usando interpolazione lineare
        
        Args:
            run: Lista di array numpy, ogni array ha shape (NUM_LANDMARKS, 4)
            target_frames: Numero target di frame
        
        Returns:
            Lista di array numpy interpolati
        """
        original_frames = len(run)
        
        if original_frames == 1:
            # Se c'è un solo frame, ripetilo
            return [run[0].copy() for _ in range(target_frames)]
        
        # Converti run in array numpy: (original_frames, NUM_LANDMARKS, 4)
        run_array = np.array(run)  # Shape: (original_frames, NUM_LANDMARKS, 4)
        
        # Indici originali (0, 1, 2, ..., original_frames-1)
        original_indices = np.arange(original_frames, dtype=np.float32)
        
        # Indici target (0, 1, 2, ..., target_frames-1) normalizzati a [0, original_frames-1]
        target_indices = np.linspace(0, original_frames - 1, target_frames)
        
        # Interpola per ogni landmark e ogni coordinata
        interpolated_run = []
        for frame_idx in target_indices:
            # Trova i due frame originali più vicini
            idx_low = int(np.floor(frame_idx))
            idx_high = int(np.ceil(frame_idx))
            
            # Clamp agli indici validi
            idx_low = max(0, min(idx_low, original_frames - 1))
            idx_high = max(0, min(idx_high, original_frames - 1))
            
            if idx_low == idx_high:
                # Esattamente su un frame originale
                interpolated_frame = run_array[idx_low].copy()
            else:
                # Interpolazione lineare tra i due frame
                alpha = frame_idx - idx_low
                interpolated_frame = (
                    (1 - alpha) * run_array[idx_low] + 
                    alpha * run_array[idx_high]
                )
            
            interpolated_run.append(interpolated_frame)
        
        return interpolated_run
    
    def compute_ghost_profile(self, runs_data: List[List[np.ndarray]], 
                             target_frames: int = None) -> Tuple[np.ndarray, np.ndarray, int, float]:
        """
        Calcola il Ghost Profile (media + tolleranze) da multiple corse
        
        Args:
            runs_data: Lista di corse, ogni corsa è una lista di array numpy (frame x landmark x 4)
            target_frames: Numero target di frame dopo normalizzazione
        
        Returns:
            Tuple contenente:
            - ghost_data: Array numpy shape (target_frames, NUM_LANDMARKS, 4) - media dei landmark
            - tolerances: Array numpy shape (target_frames, NUM_LANDMARKS, 4) - deviazioni standard
            - best_run_index: Indice (0-4) della corsa più vicina alla media
            - best_run_distance: Distanza euclidea della best run
        """
        if len(runs_data) != 5:
            raise ValueError(f"Devono esserci esattamente 5 corse, trovate {len(runs_data)}")
        
        # Salva lunghezze originali
        original_frame_counts = [len(run) for run in runs_data]
        
        # Normalizza temporalmente
        normalized_runs = self.normalize_temporal(runs_data, target_frames)
        target_frames = len(normalized_runs[0])
        
        # Converti in array numpy: (5, target_frames, NUM_LANDMARKS, 4)
        runs_array = np.array(normalized_runs)  # Shape: (5, target_frames, NUM_LANDMARKS, 4)
        
        # Calcola media punto per punto (asse 0 = corse)
        ghost_data = np.mean(runs_array, axis=0)  # Shape: (target_frames, NUM_LANDMARKS, 4)
        
        # Calcola deviazione standard (tolleranze)
        tolerances = np.std(runs_array, axis=0)  # Shape: (target_frames, NUM_LANDMARKS, 4)
        
        # Assicurati che le tolleranze non siano zero (minimo 1e-6)
        tolerances = np.maximum(tolerances, 1e-6)
        
        # Trova Best Run: confronta ogni corsa normalizzata con la media
        best_run_index = 0
        best_run_distance = float('inf')
        
        for i, normalized_run in enumerate(normalized_runs):
            # Calcola distanza euclidea totale tra questa corsa e la media
            run_array = np.array(normalized_run)  # Shape: (target_frames, NUM_LANDMARKS, 4)
            
            # Differenza punto per punto
            diff = run_array - ghost_data  # Shape: (target_frames, NUM_LANDMARKS, 4)
            
            # Distanza euclidea per ogni frame (somma su landmark e coordinate)
            # Usa solo x, y, z (ignora visibility per la distanza)
            frame_distances = np.sqrt(np.sum(diff[:, :, :3] ** 2, axis=(1, 2)))  # Shape: (target_frames,)
            
            # Distanza totale (somma su tutti i frame)
            total_distance = np.sum(frame_distances)
            
            logger.debug(f"  Run {i}: distanza totale = {total_distance:.6f}")
            
            if total_distance < best_run_distance:
                best_run_distance = total_distance
                best_run_index = i
        
        logger.info(f"🏆 Best Run: indice {best_run_index}, distanza = {best_run_distance:.6f}")
        
        return ghost_data, tolerances, best_run_index, best_run_distance
    
    def analyze_run(self, run_data: List[np.ndarray], 
                   ghost_data: np.ndarray, 
                   tolerances: np.ndarray) -> Tuple[float, float, float, List[float]]:
        """
        Analizza una nuova corsa confrontandola con il Ghost Profile
        
        Args:
            run_data: Lista di array numpy (frame x landmark x 4) della nuova corsa
            ghost_data: Array numpy shape (target_frames, NUM_LANDMARKS, 4) - Ghost Profile
            tolerances: Array numpy shape (target_frames, NUM_LANDMARKS, 4) - Tolleranze
        
        Returns:
            Tuple contenente:
            - total_error: Errore totale (somma distanze euclidee)
            - mean_error: Errore medio per frame
            - max_error: Errore massimo per frame
            - frame_errors: Lista di errori per ogni frame
        """
        # Normalizza temporalmente la nuova corsa alla stessa lunghezza del ghost
        target_frames = len(ghost_data)
        normalized_run = self._interpolate_run(run_data, target_frames)
        run_array = np.array(normalized_run)  # Shape: (target_frames, NUM_LANDMARKS, 4)
        
        # Calcola differenza punto per punto
        diff = run_array - ghost_data  # Shape: (target_frames, NUM_LANDMARKS, 4)
        
        # Distanza euclidea per ogni frame (solo x, y, z)
        frame_errors = np.sqrt(np.sum(diff[:, :, :3] ** 2, axis=(1, 2)))  # Shape: (target_frames,)
        
        total_error = float(np.sum(frame_errors))
        mean_error = float(np.mean(frame_errors))
        max_error = float(np.max(frame_errors))
        
        return total_error, mean_error, max_error, frame_errors.tolist()
    
    def convert_to_numpy(self, run_data) -> List[np.ndarray]:
        """
        Converte RunData (Pydantic) in formato numpy per processing
        
        Args:
            run_data: RunData (Pydantic model)
        
        Returns:
            Lista di array numpy, ogni array ha shape (NUM_LANDMARKS, 4)
        """
        numpy_run = []
        for frame in run_data.frames:
            frame_array = np.zeros((self.NUM_LANDMARKS, 4), dtype=np.float32)
            for i, landmark in enumerate(frame.landmarks):
                frame_array[i, 0] = landmark.x
                frame_array[i, 1] = landmark.y
                frame_array[i, 2] = landmark.z
                frame_array[i, 3] = landmark.visibility
            numpy_run.append(frame_array)
        return numpy_run
    
    def convert_from_numpy(self, ghost_data: np.ndarray, tolerances: np.ndarray) -> Tuple[List, List]:
        """
        Converte array numpy in formato Pydantic
        
        Args:
            ghost_data: Array numpy shape (frames, NUM_LANDMARKS, 4)
            tolerances: Array numpy shape (frames, NUM_LANDMARKS, 4)
        
        Returns:
            Tuple (ghost_landmarks, tolerance_objects) - media su tutti i frame
        """
        # Media su tutti i frame per ottenere un singolo "ghost" rappresentativo
        # Questo semplifica il modello: un ghost è rappresentato da 33 landmark medi
        ghost_mean = np.mean(ghost_data, axis=0)  # Shape: (NUM_LANDMARKS, 4)
        tolerance_mean = np.mean(tolerances, axis=0)  # Shape: (NUM_LANDMARKS, 4)
        
        ghost_landmarks = []
        tolerance_objects = []
        
        # Import locale per evitare circular imports
        # Supporta sia esecuzione diretta che import come package
        try:
            from .models import Landmark, Tolerance
        except ImportError:
            from math_engine.models import Landmark, Tolerance
        
        for i in range(self.NUM_LANDMARKS):
            ghost_landmarks.append(Landmark(
                x=float(ghost_mean[i, 0]),
                y=float(ghost_mean[i, 1]),
                z=float(ghost_mean[i, 2]),
                visibility=float(ghost_mean[i, 3])
            ))
            tolerance_objects.append(Tolerance(
                x=float(tolerance_mean[i, 0]),
                y=float(tolerance_mean[i, 1]),
                z=float(tolerance_mean[i, 2]),
                visibility=float(tolerance_mean[i, 3])
            ))
        
        return ghost_landmarks, tolerance_objects

