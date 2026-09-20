import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

# 1. Define the Multi-Lead Deep Learning Convolutional Network
class MultiLeadECGClassifier(nn.Module):
    """
    Advanced 1D Convolutional Neural Network (CNN) designed to ingest 
    3-lead simultaneous ECG time-series signal records and classify 
    underlying patient cardiac rhythms.
    """
    def __init__(self, num_leads=3, num_classes=3):
        super(MultiLeadECGClassifier, self).__init__()
        
        # Convolutional Block 1: Extracts spatial morphology across channels
        self.conv1 = nn.Conv1d(in_channels=num_leads, out_channels=32, kernel_size=7, padding=3)
        self.bn1 = nn.BatchNorm1d(32)
        
        # Convolutional Block 2: Downsamples resolution while sharpening features
        self.conv2 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=5, padding=2)
        self.bn2 = nn.BatchNorm1d(64)
        
        # Adaptive pooling ensures a constant feature footprint regardless of sequence length
        self.pool = nn.AdaptiveMaxPool1d(8)
        
        # Fully Connected Classification Classifier Heads
        self.fc1 = nn.Linear(64 * 8, 128)
        self.dropout = nn.Dropout(p=0.3)
        self.fc2 = nn.Linear(128, num_classes)
        
    def forward(self, x):
        # Input shape constraint verification: (Batch, Channels/Leads, Sequence Length)
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.max_pool1d(x, kernel_size=2)
        
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool(x)
        
        # Flatten feature matrices before passing to dense arrays
        x = x.view(x.size(0), -1)
        
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x) # Returns raw unnormalized logits
        return x

# 2. Pipeline Utility Runner Engine
def execute_predictive_diagnostics(input_waveform_array: np.ndarray) -> dict:
    """
    Wrapper function that accepts raw multidimensional numpy array feeds,
    converts them to PyTorch evaluation tensors, and predicts cardiac condition probabilities.
    """
    # Initialize labels definition dictionary
    diagnostic_classes = {0: "NORMAL_SINUS_RHYTHM", 1: "ATRIAL_FIBRILLATION", 2: "VENTRICULAR_ARRHYTHMIA"}
    
    # 1. Instantiate network architecture and configure evaluation settings
    model = MultiLeadECGClassifier(num_leads=3, num_classes=3)
    model.eval()
    
    # 2. Reshape and load raw data safely into execution tensors
    # Expected shape conversion -> (Batch=1, Leads=3, Timesteps=200)
    tensor_signal = torch.tensor(input_waveform_array, dtype=torch.float32).unsqueeze(0)
    
    with torch.no_grad():
        logits = model(tensor_signal)
        probabilities = F.softmax(logits, dim=1).numpy()[0]
        
    # 3. Compile output telemetry mapping profile
    highest_match_idx = int(np.argmax(probabilities))
    
    return {
        "model_architecture": "1D-MultiLead-CNN-v1",
        "primary_diagnostic_prediction": diagnostic_classes[highest_match_idx],
        "confidence_score": float(probabilities[highest_match_idx]),
        "probability_distribution": {diagnostic_classes[i]: float(probabilities[i]) for i in range(len(probabilities))}
    }

if __name__ == "__main__":
    print("🧠 Initializing Deep Learning Multi-Lead Classification Model Subsystem...")
    
    # Synthesize dummy evaluation matrix block: 3 leads, 200 data voltage metrics sequence timesteps
    mock_leads_data = np.random.randn(3, 200)
    
    results = execute_predictive_diagnostics(mock_leads_data)
    print("\n🔬 INFERENCE RUN RESOLUTION MATRIX LOGS:")
    print(f" -> Predicted Status: {results['primary_diagnostic_prediction']}")
    print(f" -> Classifier Confidence Match Score: {results['confidence_score']:.4f}")
    print(f" -> Probabilities List Summary: {results['probability_distribution']}")
