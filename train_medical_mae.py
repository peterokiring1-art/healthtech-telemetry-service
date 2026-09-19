import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from medical_mae import MedicalSignalMAE  # Reuses your verified architecture

def generate_pretraining_dataset(num_samples=1000, signal_length=500):
    """
    Generates a synthetic physiological training set.
    Simulates base sinus rhythms so the model learns 'normal' biology.
    """
    print(f"📦 Synthesizing {num_samples} clinical waveform arrays for pre-training...")
    t = np.linspace(0, 1, signal_length)
    data = []
    
    for _ in range(num_samples):
        # Base heart rhythm wave component
        frequency = np.random.uniform(1.0, 2.0) 
        heartbeat = np.sin(2 * np.pi * frequency * t)
        
        # Add random subtle phase shifts and minor baseline wander
        phase = np.random.uniform(0, np.pi)
        heartbeat += 0.5 * np.sin(2 * np.pi * 0.2 * t + phase)
        
        # Add high-frequency sensor noise
        noise = np.random.normal(0, 0.05, signal_length)
        
        data.append(heartbeat + noise)
        
    data_array = np.array(data, dtype=np.float32)
    # Reshape to [Samples, Channels, Length] for 1D PyTorch Conv layers
    data_tensor = torch.from_numpy(data_array).unsqueeze(1)
    return data_tensor

def train_foundation_model():
    # 1. Hyperparameters & Hardware Configuration
    epochs = 5
    batch_size = 32
    learning_rate = 1e-3
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️ Training execution environment target: {device}")

    # 2. Data Preparation
    raw_tensors = generate_pretraining_dataset()
    dataset = TensorDataset(raw_tensors)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # 3. Model Initialization
    model = MedicalSignalMAE(signal_length=500).to(device)
    criterion = nn.MSELoss()
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)

    # 4. Active Training Loop
    print("\n🚀 Commencing Self-Supervised Pretext Training Loop...")
    model.train()
    
    for epoch in range(1, epochs + 1):
        running_loss = 0.0
        
        for batch_idx, (batch_data,) in enumerate(dataloader):
            batch_data = batch_data.to(device)
            
            # Zero out gradients from the previous step
            optimizer.zero_grad()
            
            # Forward pass: apply random masking internally and reconstruct
            reconstructed, _ = model(batch_data)
            
            # Compute loss against the original clean target waveform
            loss = criterion(reconstructed, batch_data)
            
            # Backward pass: compute gradients and update weights
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
        epoch_loss = running_loss / len(dataloader)
        print(f"📊 Epoch [{epoch}/{epochs}] Complete -> Average Reconstruction Loss: {epoch_loss:.4f}")

    # 5. Serialize Model Weights
    weight_path = "medical_mae_weights.pth"
    torch.save(model.state_dict(), weight_path)
    print(f"\n💾 Model weights safely saved to disk at: '{weight_path}'")

if __name__ == "__main__":
    train_foundation_model()
