import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# 1. Define the 1D Deep Masked Autoencoder Architecture
class MedicalSignalMAE(nn.Module):
    def __init__(self, signal_length=500):
        super(MedicalSignalMAE, self).__init__()
        self.signal_length = signal_length
        
        # Encoder: Compresses the unmasked signal segments into abstract representations
        self.encoder = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=15, stride=2, padding=7), # [batch, 16, 250]
            nn.BatchNorm1d(16),
            nn.ReLU(),
            nn.Conv1d(16, 32, kernel_size=7, stride=2, padding=3), # [batch, 32, 125]
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Conv1d(32, 64, kernel_size=3, stride=2, padding=1), # [batch, 64, 63]
            nn.BatchNorm1d(64),
            nn.ReLU()
        )
        
        # Decoder: Generative upsampling layers to reconstruct the absolute waveform
        self.decoder = nn.Sequential(
            nn.ConvTranspose1d(64, 32, kernel_size=3, stride=2, padding=1, output_padding=0), # [batch, 32, 125]
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.ConvTranspose1d(32, 16, kernel_size=7, stride=2, padding=3, output_padding=1), # [batch, 16, 250]
            nn.BatchNorm1d(16),
            nn.ReLU(),
            nn.ConvTranspose1d(16, 1, kernel_size=15, stride=2, padding=7, output_padding=1), # [batch, 1, 500]
        )

    def apply_mask(self, x, mask_ratio=0.25):
        """Randomly masks sequential fragments of the physiological array to challenge the network."""
        batch_size, channels, length = x.shape
        masked_x = x.clone()
        mask_len = int(length * mask_ratio)
        
        # Apply a distinct random mask block for every item in the processing batch
        for i in range(batch_size):
            start_idx = np.random.randint(0, length - mask_len)
            masked_x[i, :, start_idx : start_idx + mask_len] = 0.0
            
        return masked_x

    def forward(self, x):
        # Apply generative self-supervised masking masking step
        masked_inputs = self.apply_mask(x)
        
        latent_features = self.encoder(masked_inputs)
        reconstructed_signal = self.decoder(latent_features)
        return reconstructed_signal, masked_inputs

# 2. Execution & Training Simulation
if __name__ == "__main__":
    print("🧠 Initializing Self-Supervised Medical Foundation Model Pipeline...")
    
    # Instantiate architecture
    model = MedicalSignalMAE(signal_length=500)
    criterion = nn.MSELoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.001)
    
    # Create 32 instances of synthetic 500Hz ECG signals [Batch, Channels, Length]
    mock_batch = torch.randn(32, 1, 500)
    
    # Forward Pass
    reconstructed, masked_inputs = model(mock_batch)
    
    # Compute self-supervised loss against original uncorrupted baseline measurements
    loss = criterion(reconstructed, mock_batch)
    
    print("✅ Model Pass Successful.")
    print(f"-> Input Telemetry Stream Shape: {mock_batch.shape}")
    print(f"-> Masked Telemetry Layer Shape: {masked_inputs.shape}")
    print(f"-> Reconstructed Signal Matrix Shape: {reconstructed.shape}")
    print(f"-> Current Pretext Reconstruction Loss: {loss.item():.4f}")
