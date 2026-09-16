import time
import random
from datetime import datetime, timezone
import urllib.request
import json

def run_telemetry_simulator():
    print("=== Clinical IoT Hardware Device Simulator Active ===")
    # Using localhost to bypass any local Windows address translation blocks
    target_url = "http://localhost:8080/api/v1/telemetry/pulseox"
    
    packet_count = 0
    while packet_count < 5:
        packet_count += 1
        print(f"\n📡 Transmitting Vital Packet #{packet_count} over airwaves...")
        
        # Fixed random syntax selection safely
        simulated_spo2 = random.choice([98, 97, 86, 95, 88]) 
        simulated_hr = random.randint(70, 115)
        
        # Clean modern UTC timestamp configuration
        payload_data = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "patient_id": "PT-777-SIM",
            "spo2": simulated_spo2,
            "heart_rate": simulated_hr
        }
        
        try:
            json_bytes = json.dumps(payload_data).encode("utf-8")
            
            req = urllib.request.Request(
                target_url, 
                data=json_bytes, 
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req) as response:
                response_text = response.read().decode("utf-8")
                parsed_res = json.loads(response_text)
                
                print(f"✅ Server Response: {parsed_res.get('status')} | Database Confirmed.")
                if parsed_res.get("alert_triggered"):
                    print("🚨 [WARNING] Server flagged an active clinical abnormality threshold alert!")
                    
        except Exception as network_err:
            print(f"❌ Transmission dropped out due to network exception: {network_err}")
            print("💡 Reminder: Make sure your Uvicorn server is running in your other terminal pane!")
            
        time.sleep(2)

if __name__ == "__main__":
    run_telemetry_simulator()
