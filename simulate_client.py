import time
import random
from datetime import datetime, timezone
import urllib.request
import json

def run_telemetry_simulator():
    print("=== Secure Clinical IoT Hardware Device Simulator Active ===")
    target_url = "http://localhost:8080/api/v1/telemetry/pulseox"
    
    # 🔐 Match the exact secret authentication credentials set on the server
    API_KEY = "healthtech-secure-token-2026"
    API_KEY_NAME = "X-API-KEY"
    
    packet_count = 0
    while packet_count < 5:
        packet_count += 1
        print(f"\n📡 Transmitting Authenticated Vital Packet #{packet_count} over airwaves...")
        
        simulated_spo2 = random.choice([98, 97, 85, 96, 89]) 
        simulated_hr = random.randint(70, 115)
        
        payload_data = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "patient_id": "PT-777-SIM",
            "spo2": simulated_spo2,
            "heart_rate": simulated_hr
        }
        
        try:
            json_bytes = json.dumps(payload_data).encode("utf-8")
            
            # 🤝 Inject the secret token safely into the HTTP headers
            req = urllib.request.Request(
                target_url, 
                data=json_bytes, 
                headers={
                    "Content-Type": "application/json",
                    API_KEY_NAME: API_KEY  # The secure signature
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req) as response:
                response_text = response.read().decode("utf-8")
                parsed_res = json.loads(response_text)
                
                print(f"✅ Server Response: {parsed_res.get('status')} | Authenticated Storage Confirmed.")
                if parsed_res.get("alert_triggered"):
                    print("🚨 [WARNING] Server flagged an active clinical abnormality threshold alert!")
                    
        except Exception as network_err:
            print(f"❌ Transmission dropped out due to network exception: {network_err}")
            
        time.sleep(2)

if __name__ == "__main__":
    run_telemetry_simulator()
