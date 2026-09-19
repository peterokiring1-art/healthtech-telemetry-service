import os
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

# --- 1. Synthesize Mock Clinical Volumetric Segmentation Data ---
def generate_mock_segmentation_pair(image_path="slice_01_img.npy", mask_path="slice_01_mask.npy"):
    """
    Generates a mock pairs for deep learning segmentation.
    Image: A simulated 256x256 organ cross-section.
    Mask: A matching binary array pinpointing the location of a lesion.
    """
    # Create background context
    img_array = np.random.normal(loc=-200.0, scale=50.0, size=(256, 256)).astype(np.float32)
    mask_array = np.zeros((256, 256), dtype=np.float32)
    
    # Inject a simulated circular tumor lesion in the upper-right quadrant
    xx, yy = np.ogrid[:256, :256]
    tumor_zone = (xx - 80)**2 + (yy - 180)**2 < 15**2
    
    img_array[tumor_zone] += 500.0  # Elevate tissue density inside the tumor zone
    mask_array[tumor_zone] = 1.0    # Set ground truth mask value to 1 for the target lesion
    
    np.save(image_path, img_array)
    np.save(mask_path, mask_array)

# --- 2. Custom PyTorch Biomedical Segmentation Dataset Wrapper ---
class BiomedicalSegmentationDataset(Dataset):
    def __init__(self, image_dir_list, mask_dir_list, transform=None):
        """
        Expects parallel lists where image_dir_list[i] matches mask_dir_list[i].
        """
        self.image_files = image_dir_list
        self.mask_files = mask_dir_list
        self.transform = transform

        if len(self.image_files) != len(self.mask_files):
            raise ValueError("❌ Structural Mismatch: The number of images must match the number of masks.")

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        # Load raw numpy arrays (simulating extraction from preprocessed DICOM files)
        raw_image = np.load(self.image_files[idx])
        raw_mask = np.load(self.mask_files[idx])

        # Step A: Min-Max Intensity Normalization for the input scan slice
        # Brings the wide density values cleanly into standard [0.0, 1.0] neural range
        img_min, img_max = raw_image.min(), raw_image.max()
        if img_max - img_min > 0:
            normalized_image = (raw_image - img_min) / (img_max - img_min)
        else:
            normalized_image = raw_image

        # Step B: Shape Alignment for PyTorch 2D Convolutions
        # Transforms standard 2D arrays [H, W] into 3D tensors [Channels, H, W]
        image_tensor = torch.from_numpy(normalized_image).unsqueeze(0).float()
        mask_tensor = torch.from_numpy(raw_mask).unsqueeze(0).float()

        return image_tensor, mask_tensor

# --- 3. Execution Driver Script ---
if __name__ == "__main__":
    print("🔬 Setting up PyTorch Biomedical Segmentation Loader...")

    img_file = "temp_slice_img.npy"
    mask_file = "temp_slice_mask.npy"
    
    # Generate simulated clinic scans
    generate_mock_segmentation_pair(img_file, mask_file)
    
    # Instantiate our new custom pipeline wrapper
    medical_dataset = BiomedicalSegmentationDataset(
        image_dir_list=[img_file],
        mask_dir_list=[mask_file]
    )
    
    # Wrap with a PyTorch DataLoader loop
    segmentation_loader = DataLoader(medical_dataset, batch_size=1, shuffle=True)
    
    # Pull a batch sample out to inspect tensor shapes
    for batch_idx, (images, masks) in enumerate(segmentation_loader):
        print("\n✅ Verification Successful. Batched Tensors verified:")
        print(f" -> Input Scan Tensor Shape:  {images.shape}  [Batch, Channel, Height, Width]")
        print(f" -> Ground-Truth Mask Shape:  {masks.shape}  [Batch, Channel, Height, Width]")
        print(f" -> Unique values in Mask:    {torch.unique(masks).tolist()} (0 = Normal, 1 = Lesion/Tumor)")
        print(f" -> Input Density Float Scale: Min={images.min().item():.2f}, Max={images.max().item():.2f}")

    # Clean local scratch space files
    for f in [img_file, mask_file]:
        if os.path.exists(f):
            os.remove(f)
