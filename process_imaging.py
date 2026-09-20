import cv2
import numpy as np
import matplotlib.pyplot as plt

def generate_and_segment_tissue():
    print("🔬 Initializing OpenCV Medical Computer Vision Pipeline...")
    
    # 1. Generate an artificial high-resolution diagnostic tissue/cell sample matrix
    canvas_size = 512
    mock_tissue = np.full((canvas_size, canvas_size), 40, dtype=np.uint8)
    
    # Render mock cell anomalies with soft contrasting intensity borders
    cv2.circle(mock_tissue, (180, 200), 55, 180, -1)  # Target Structure Alpha
    cv2.circle(mock_tissue, (340, 320), 40, 210, -1)  # Target Structure Beta
    
    # Inject high-frequency white noise to replicate sensor scatter interference
    noise = np.random.normal(0, 15, mock_tissue.shape).astype(np.float64)
    noisy_tissue = np.clip(mock_tissue.astype(np.float64) + noise, 0, 255).astype(np.uint8)
    
    # 2. De-noise data using localized spatial Gaussian blur operations
    de_noised_tissue = cv2.GaussianBlur(noisy_tissue, (9, 9), 0)
    
    # 3. Apply Otsu's Adaptive Thresholding Segmentation
    # This automatically computes an optimized global binarization split limit
    _, segmented_binary = cv2.threshold(de_noised_tissue, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 4. Isolate spatial feature edges using the Canny Structural Edge Detection algorithm
    structural_edges = cv2.Canny(de_noised_tissue, 50, 150)
    
    print("🏁 Image segmentation maps and structural boundary matrices computed successfully.")
    
    # 5. Render Matrix Grid Subplots for Visual Inspection (Fixed Unpacking array bug)
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(16, 5))
    
    ax1.imshow(noisy_tissue, cmap='gray')
    ax1.set_title("1. Raw Scan Input Data")
    ax1.axis('off')
    
    ax2.imshow(de_noised_tissue, cmap='gray')
    ax2.set_title("2. Gaussian De-noised")
    ax2.axis('off')
    
    ax3.imshow(segmented_binary, cmap='jet')
    ax3.set_title("3. Otsu Segmented Masks")
    ax3.axis('off')
    
    ax4.imshow(structural_edges, cmap='gray')
    ax4.set_title("4. Extracted Edge Outlines")
    ax4.axis('off')
    
    plt.suptitle("Phase 2 Testing: 2D Spatial Computer Vision Preprocessing Pipeline")
    plt.tight_layout()
    
    output_filename = "medical_imaging_output.png"
    plt.savefig(output_filename)
    print(f"💾 Visual image segmentation verification matrix saved as: '{output_filename}'")
    plt.close()

if __name__ == "__main__":
    generate_and_segment_tissue()
