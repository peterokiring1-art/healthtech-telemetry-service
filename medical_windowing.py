import numpy as np

def generate_chest_ct_slice():
    """
    Synthesizes a realistic cross-sectional thoracic CT matrix in raw Hounsfield Units (HU).
    Air: -1000 HU | Lungs: -700 HU | Fat/Muscle: -50 to +50 HU | Bone/Tumor: +400 to +1000 HU
    """
    # 1. Start with an open air-filled scanner background
    ct_matrix = np.full((512, 512), -1000.0, dtype=np.float32)
    
    # 2. Simulate chest wall/soft tissue ring (around 0 HU)
    yy, xx = np.ogrid[:512, :512]
    body_mask = (yy - 256)**2 + (xx - 256)**2 < 200**2
    ct_matrix[body_mask] = 20.0
    
    # 3. Simulate two lung cavities (air filled tissue, around -700 HU)
    left_lung = (yy - 256)**2 + (xx - 180)**2 < 80**2
    right_lung = (yy - 256)**2 + (xx - 332)**2 < 80**2
    ct_matrix[left_lung] = -700.0
    ct_matrix[right_lung] = -700.0
    
    # 4. Simulate dense spinal bone (+800 HU) at the posterior wall
    spine = (yy - 420)**2 + (xx - 256)**2 < 25**2
    ct_matrix[spine] = 800.0
    
    # 5. Simulate a structural tissue anomaly/lesion (+350 HU) hidden inside the dark left lung
    lesion = (yy - 220)**2 + (xx - 160)**2 < 12**2
    ct_matrix[lesion] = 350.0
    
    return ct_matrix

def apply_clinical_window(hu_matrix, window_width, window_level):
    """
    Applies radiographic contrast windowing transforms.
    Clamps the matrix to the window bounds and scales linearly to standard 8-bit visual arrays.
    """
    # Calculate lower and upper boundary limits in Hounsfield Units
    lower_bound = window_level - (window_width / 2.0)
    upper_bound = window_level + (window_width / 2.0)
    
    # Clamp the raw density arrays to target physiological visibility limits
    clamped_matrix = np.clip(hu_matrix, lower_bound, upper_bound)
    
    # Rescale the windowed segment linearly to common display ranges [0.0, 255.0]
    normalized = (clamped_matrix - lower_bound) / (upper_bound - lower_bound)
    visual_gray_matrix = (normalized * 255.0).astype(np.uint8)
    
    return visual_gray_matrix

if __name__ == "__main__":
    print("🩻 Initializing Advanced Radiographic Windowing Engine...")
    
    # Ingest the simulated raw scanner matrix
    raw_ct = generate_chest_ct_slice()
    print(f" -> Raw CT Slice Matrix Shape: {raw_ct.shape}")
    print(f" -> Full Dynamic Range in HU: Min={raw_ct.min():.1f} HU, Max={raw_ct.max():.1f} HU\n")
    
    # Define industry-standard clinical window profiles
    windows = {
        "Lung Window (Isolates pulmonary nodules/tissue)": {"WW": 1500, "WL": -600},
        "Soft Tissue / Mediastinum Window (Isolates muscles/organs)": {"WW": 350, "WL": 50},
        "Bone Window (Isolates fractures/skeletal anomalies)": {"WW": 2000, "WL": 500}
    }
    
    for title, params in windows.items():
        ww = params["WW"]
        wl = params["WL"]
        
        # Execute contrast window adjustment
        visual_slice = apply_clinical_window(raw_ct, window_width=ww, window_level=wl)
        
        # Diagnostics to prove target structural anomalies are visible vs hidden
        # We look at the coordinates of our simulated lesion inside the left lung (row 220, col 160)
        lesion_pixel_val = visual_slice[220, 160]
        lung_pixel_val = visual_slice[256, 180]
        
        print(f"🎬 Applied Profile: {title} [Width: {ww}, Level: {wl}]")
        print(f"   -> Normal Lung Gray-Level:  {lung_pixel_val}/255")
        print(f"   -> Lesion/Anomaly Gray-Level: {lesion_pixel_val}/255")
        
        # Visual analysis check
        contrast_gap = int(lesion_pixel_val) - int(lung_pixel_val)
        if contrast_gap > 200:
            print("   💡 ANALYSIS: The anomaly stands out clearly against the lung backdrop (High Contrast).")
        elif lesion_pixel_val == 255 and lung_pixel_val == 255:
            print("   ❌ ANALYSIS: The anomaly is completely washed out (Pure White oversaturation).")
        else:
            print("   ⚠️ ANALYSIS: Low contrast variation. Structural boundaries are visually obscured.")
        print("-" * 75)
