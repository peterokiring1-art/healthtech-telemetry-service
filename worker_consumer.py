import os
import json
import time
import pika
from init_db import SessionLocal, PatientTelemetryModel, initialize_database_tables

def start_event_stream_consumer():
    print("👷 Establishing connection to centralized RabbitMQ message cluster...")
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "127.0.0.1")
    
    # Simple retry loop to handle startup race conditions during container boots
    for retry in range(1, 11):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            break
        except Exception:
            print(f"⚠️ Broker not ready yet. Retrying loop ({retry}/10)...")
            time.sleep(5)
            
    channel = connection.channel()
    channel.queue_declare(queue='telemetry_stream_queue', durable=True)
    
    def process_incoming_message(ch, method, properties, body):
        try:
            data = json.loads(body.decode('utf-8'))
            db_session = SessionLocal()
            try:
                db_record = PatientTelemetryModel(
                    patient_id=data["patient_id"],
                    spo2=data["spo2"],
                    heart_rate=data["heart_rate"],
                    raw_timestamp=data["timestamp"]
                )
                db_session.add(db_record)
                db_session.commit()
                print(f"💾 [EVENT CONSUMER] Successfully committed SQL record for: {data['patient_id']}")
            except Exception as e:
                db_session.rollback()
                print(f"❌ SQL Insertion Rollback: {str(e)}")
            finally:
                db_session.close()
        except Exception as parse_error:
            print(f"❌ Message parsing failure: {str(parse_error)}")
            
        # Send manual acknowledgment back to RabbitMQ that message is safely handled
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # Configure fair dispatching: distribute only 1 packet at a time to workers
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='telemetry_stream_queue', on_message_callback=process_incoming_message)
    
    print("🚀 Event Consumer Active! Listening for live incoming RabbitMQ event logs...")
    channel.start_consuming()

if __name__ == "__main__":
    # Ensure tables exist on database initialization boot
    time.sleep(5) # Allow database container to initialize first
    initialize_database_tables()
    start_event_stream_consumer()
