import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import matplotlib.pyplot as plt

# 1. Define the 1D Deep Learning Architecture
class Biomedical1DCNN(nn.Module):
    def __init__(self):
        super(Biomedical1DCNN, self).__init__()
        # Conv1d expects input shape: (batch_size, num_channels, sequence_length)
        self.feature_extractor = nn.Sequential(
            nn.Conv1d(in_channels=1, out_channels=16, kernel_size=7, stride=1, padding=3),
            nn.BatchNorm1d(16),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2), # Halves sequence feature length
            
            nn.Conv1d(in_channels=16, out_channels=32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2)  # Halves length again
        )
        
        # Sequence input length of 180 becomes 45 after two MaxPool1d operations (180 / 2 / 2)
        self.classification_head = nn.Sequential(
            nn.Linear(32 * 45, 64),
            nn.ReLU(),
            nn.Dropout(p=0.3), # Prevents model overfitting
            nn.Linear(64, 2)   # 2 Output Neurons: Class 0 (Normal Rhythm) vs Class 1 (Arrhythmia)
        )

    def forward(self, x):
        x = self.feature_extractor(x)
        x = x.view(x.size(0), -1) # Flatten out multidimensional channel matrices to vector
        logits = self.classification_head(x)
        return logits

# 2. Local Simulation Data Generator (Balanced Clinical Sample Simulation)
def generate_synthetic_dataset(num_samples=200, seq_len=180):
    np.random.seed(42)
    data = []
    labels = []
    
    for i in range(num_samples):
        label = np.random.choice([0, 1]) # 0 = Normal, 1 = Arrhythmia
        time = np.linspace(0, 1, seq_len)
        
        if label == 0:
            # Base Normal Signal: Smooth, regular baseline heartbeat pulse
            pulse = np.sin(2 * np.pi * 2 * time) + 0.5 * np.sin(2 * np.pi * 5 * time)
        else:
            # Arrhythmic Anomaly Signal: Erratic frequency oscillation and spike variations
            pulse = np.sin(2 * np.pi * 4 * time) + np.sin(2 * np.pi * 12 * time)
            
        # Add baseline sensor thermal white noise
        noise = np.random.normal(0, 0.3, seq_len)
        signal = pulse + noise
        
        data.append(signal)
        labels.append(label)
        
    # Reshape matching PyTorch Conv1d format constraints: (samples, channels, length)
    data_np = np.array(data, dtype=np.float32).reshape(num_samples, 1, seq_len)
    labels_np = np.array(labels, dtype=np.int64)
    
    return torch.tensor(data_np), torch.tensor(labels_np)

# 3. Main Model Execution and Training Pipeline Routine
def train_pipeline():
    print("🧠 Initializing PyTorch 1D CNN Arrhythmia Classification Network...")
    
    # Setup hyperparameters
    epochs = 15
    batch_size = 32
    learning_rate = 0.001
    
    # Generate and compile data structures
    X, y = generate_synthetic_dataset(num_samples=240, seq_len=180)
    
    # Execute an 80/20 train/validation split
    split_index = int(0.8 * len(X))
    train_ds = TensorDataset(X[:split_index], y[:split_index])
    val_ds = TensorDataset(X[split_index:], y[split_index:])
    
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    
    # Instantiate net nodes and tracking entities
    model = Biomedical1DCNN()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    loss_history = []
    
    print(f"🚀 Training network across {epochs} epochs over background tensor batch loops...")
    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        
        for batch_inputs, batch_labels in train_loader:
            optimizer.zero_grad() # Flush out residual gradient steps from past traces
            
            outputs = model(batch_inputs)
            loss = criterion(outputs, batch_labels)
            
            loss.backward()  # Backpropagation execution
            optimizer.step()  # Update network neural synapse weights
            
            running_loss += loss.item() * batch_inputs.size(0)
            
        epoch_loss = running_loss / len(train_loader.dataset)
        loss_history.append(epoch_loss)
        
        # Check validation accuracy periodically
        model.eval()
        correct = 0
        with torch.no_grad():
            for val_inputs, val_labels in val_loader:
                val_outputs = model(val_inputs)
                _, preds = torch.max(val_outputs, 1)
                correct += (preds == val_labels).sum().item()
        val_acc = (correct / len(val_loader.dataset)) * 100
        
        print(f"   - Epoch [{epoch:d}/{epochs}] -> Training Loss: {epoch_loss:.4f} | Validation Accuracy: {val_acc:.1f}%")

    print("🏁 Neural Network training optimization complete.")
    
    # 4. Save trained model state dictionary weights
    model_weight_path = "arrhythmia_model_weights.pth"
    torch.save(model.state_dict(), model_weight_path)
    print(f"💾 Trained model network weights successfully saved to: '{model_weight_path}'")
    
    # 5. Render Loss Optimization Trajectory Plot
    plt.figure(figsize=(8, 4))
    plt.plot(range(1, epochs + 1), loss_history, marker='o', color='crimson', linewidth=2)
    plt.title("Phase 2 Neural Net Validation: 1D Conv1D Training Loss Convergence")
    plt.xlabel("Training Epoch Run")
    plt.ylabel("Cross-Entropy Loss Scale")
    plt.grid(True, linestyle="--", alpha=0.5)
    
    output_plot_path = "pytorch_training_loss.png"
    plt.savefig(output_plot_path)
    print(f"💾 Loss convergence graphic validation plot saved to: '{output_plot_path}'")
    plt.close()

if __name__ == "__main__":
    train_pipeline()
