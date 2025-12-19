"""
Esempio di utilizzo del Math Engine API
"""
import requests
import json

# URL del servizio (modifica se necessario)
BASE_URL = "http://localhost:8000"


def create_sample_landmark(x: float, y: float, z: float, visibility: float = 1.0) -> dict:
    """Crea un landmark di esempio"""
    return {
        "x": x,
        "y": y,
        "z": z,
        "visibility": visibility
    }


def create_sample_frame(landmarks: list = None) -> dict:
    """Crea un frame di esempio con 33 landmark"""
    if landmarks is None:
        # Crea 33 landmark di esempio (tutti zero)
        landmarks = [create_sample_landmark(0.0, 0.0, 0.0, 0.0) for _ in range(33)]
    
    return {
        "landmarks": landmarks
    }


def create_sample_run(num_frames: int = 10) -> dict:
    """Crea una corsa di esempio con num_frames frame"""
    frames = []
    for i in range(num_frames):
        # Crea landmark con valori variabili per simulare movimento
        landmarks = []
        for j in range(33):
            landmarks.append(create_sample_landmark(
                x=0.5 + 0.1 * (i / num_frames) * (j / 33),
                y=0.6 + 0.1 * (i / num_frames) * (j / 33),
                z=0.1 + 0.05 * (i / num_frames),
                visibility=0.9
            ))
        frames.append(create_sample_frame(landmarks))
    
    return {
        "frames": frames
    }


def test_compute_ghost_profile():
    """Test endpoint compute-ghost-profile"""
    print("=" * 60)
    print("TEST: Compute Ghost Profile")
    print("=" * 60)
    
    # Crea 5 corse di esempio con lunghezze diverse
    runs = []
    for i in range(5):
        num_frames = 10 + i * 2  # Lunghezze diverse: 10, 12, 14, 16, 18
        run = create_sample_run(num_frames)
        runs.append(run)
        print(f"  Run {i}: {num_frames} frame")
    
    request_data = {
        "runs": runs,
        "target_frames": 15  # Normalizza a 15 frame
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/compute-ghost-profile",
            json=request_data
        )
        response.raise_for_status()
        
        result = response.json()
        print(f"\n✅ Success!")
        print(f"  Best Run Index: {result['best_run_index']}")
        print(f"  Best Run Distance: {result['best_run_distance']:.6f}")
        print(f"  Normalized Frame Count: {result['normalized_frame_count']}")
        print(f"  Original Frame Counts: {result['original_frame_counts']}")
        print(f"  Ghost Data: {len(result['ghost_data'])} landmark")
        print(f"  Tolerances: {len(result['tolerances'])} landmark")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text}")
        return None


def test_analyze_run(ghost_profile: dict):
    """Test endpoint analyze-run"""
    print("\n" + "=" * 60)
    print("TEST: Analyze Run")
    print("=" * 60)
    
    # Crea una nuova corsa di esempio
    new_run = create_sample_run(num_frames=12)
    
    request_data = {
        "run_data": new_run,
        "ghost_profile": ghost_profile
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/analyze-run",
            json=request_data
        )
        response.raise_for_status()
        
        result = response.json()
        print(f"\n✅ Success!")
        print(f"  Total Error: {result['total_error']:.6f}")
        print(f"  Mean Error: {result['mean_error']:.6f}")
        print(f"  Max Error: {result['max_error']:.6f}")
        print(f"  Frame Errors: {len(result['frame_errors'])} frame")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text}")
        return None


def test_health():
    """Test health check"""
    print("=" * 60)
    print("TEST: Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        print(f"✅ Service is healthy: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("Math Engine API - Example Usage")
    print(f"Base URL: {BASE_URL}\n")
    
    # Test health check
    if not test_health():
        print("\n⚠️  Service is not available. Make sure it's running on", BASE_URL)
        exit(1)
    
    # Test compute ghost profile
    ghost_profile = test_compute_ghost_profile()
    
    # Test analyze run (se ghost profile è disponibile)
    if ghost_profile:
        test_analyze_run(ghost_profile)
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

