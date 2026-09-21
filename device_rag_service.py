import sqlite3
from datetime import datetime

RAG_DB_PATH = "device_knowledge_base.db"
HISTORY_DB_PATH = "field_solved_knowledge.db"

def initialize_knowledge_base():
    """Initializes tables for factory documentation, field fixes, and preventive schedules."""
    conn = sqlite3.connect(RAG_DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS device_manual_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_model TEXT NOT NULL,
            section_title TEXT,
            content TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

    conn2 = sqlite3.connect(HISTORY_DB_PATH)
    cur2 = conn2.cursor()
    # Core maintenance logging table
    cur2.execute("""
        CREATE TABLE IF NOT EXISTS historical_fixes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_model TEXT NOT NULL,
            error_code TEXT NOT NULL,
            technician_fix TEXT NOT NULL,
            date_logged TEXT NOT NULL
        );
    """)
    # New PPM scheduling table mapping intervals and calibration compliance status
    cur2.execute("""
        CREATE TABLE IF NOT EXISTS ppm_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_model TEXT NOT NULL,
            serial_number TEXT NOT NULL,
            next_ppm_date TEXT NOT NULL,
            assigned_tech TEXT NOT NULL,
            status TEXT NOT NULL
        );
    """)
    conn2.commit()
    conn2.close()

def save_manual_chunk(machine_model: str, section_title: str, text_content: str):
    initialize_knowledge_base()
    conn = sqlite3.connect(RAG_DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO device_manual_chunks (machine_model, section_title, content) VALUES (?, ?, ?);", 
                (machine_model, section_title, text_content))
    conn.commit()
    conn.close()

def process_uploaded_file(selected_model, file_obj) -> int:
    initialize_knowledge_base()
    chunks_saved = 0
    file_ext = file_obj.name.split(".")[-1].lower()
    
    # Delayed import of heavy libraries to optimize startup metrics
    if file_ext == "pdf":
        from pypdf import PdfReader
        reader = PdfReader(file_obj)
        for page_num in range(len(reader.pages)):
            page_text = reader.pages[page_num].extract_text()
            if page_text and page_text.strip():
                save_manual_chunk(selected_model, f"[{file_obj.name}] Page {page_num + 1}", page_text.strip())
                chunks_saved += 1
    elif file_ext == "docx":
        from docx import Document
        doc = Document(file_obj)
        full_text = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
        if full_text:
            save_manual_chunk(selected_model, f"[{file_obj.name}] Word Contents", "\n".join(full_text))
            chunks_saved += 1
            
    return chunks_saved

def save_successful_fix(machine_model: str, error_code: str, technician_fix: str):
    initialize_knowledge_base()
    conn = sqlite3.connect(HISTORY_DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO historical_fixes (machine_model, error_code, technician_fix, date_logged)
        VALUES (?, ?, ?, ?);
    """, (machine_model, error_code.strip().upper(), technician_fix.strip(), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def save_ppm_schedule(machine_model: str, serial_number: str, next_ppm_date: str, assigned_tech: str, status: str):
    """Logs a Planned Preventive Maintenance tracking index row onto local database lines."""
    initialize_knowledge_base()
    conn = sqlite3.connect(HISTORY_DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ppm_schedules (machine_model, serial_number, next_ppm_date, assigned_tech, status)
        VALUES (?, ?, ?, ?, ?);
    """, (machine_model, serial_number.strip().upper(), next_ppm_date, assigned_tech.strip(), status))
    conn.commit()
    conn.close()

def get_all_ppm_schedules() -> list:
    initialize_knowledge_base()
    conn = sqlite3.connect(HISTORY_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT machine_model, serial_number, next_ppm_date, assigned_tech, status FROM ppm_schedules ORDER BY next_ppm_date ASC;")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_reliability_metrics() -> dict:
    """Aggregates logged failure codes per machine class to build analytical graphs natively."""
    initialize_knowledge_base()
    conn = sqlite3.connect(HISTORY_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT machine_model, COUNT(*) FROM historical_fixes GROUP BY machine_model;")
    rows = cur.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def query_and_analyze_fault(machine_model: str, query_keyword: str, user_suggestion: str = "") -> str:
    initialize_knowledge_base()
    
    conn_hist = sqlite3.connect(HISTORY_DB_PATH)
    cur_hist = conn_hist.cursor()
    cur_hist.execute("""
        SELECT technician_fix, date_logged FROM historical_fixes 
        WHERE machine_model = ? AND error_code = ?;
    """, (machine_model, query_keyword.strip().upper()))
    past_fixes = cur_hist.fetchall()
    cur_hist.close()
    conn_hist.close()

    conn = sqlite3.connect(RAG_DB_PATH)
    cur = conn.cursor()
    cleaned_query = query_keyword.replace("-", " ").replace("_", " ")
    words = [w.strip() for w in cleaned_query.split() if len(w.strip()) > 0]
    if not words: words = [query_keyword]
    
    base_query = "SELECT section_title, content FROM device_manual_chunks WHERE machine_model = ?"
    conditions = []
    params = [machine_model]
    for word in words:
        conditions.append("(content LIKE ? OR section_title LIKE ?)")
        pattern = f"%{word}%"
        params.extend([pattern, pattern])
    full_query = f"{base_query} AND ({' AND '.join(conditions)})"
    cur.execute(full_query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    model_upper = machine_model.upper()
    if "LABORATORY" in model_upper:
        sys_type = "Automated Clinical Laboratory Platform"
        deduction = "* Fluidic Pathway: Check microfluidic lines for blocks, syringe pumps, and clean sample probes.\n* Optical Path: Verify photometer sensors and flow-cell lenses."
    elif "RADIOLOGY" in model_upper:
        sys_type = "Diagnostic Medical Imaging Modality"
        deduction = "* Electrical Bus: Verify high-voltage lines, panel shields, and test cooling fan parameters.\n* Signal Check: Inspect RF coils, gantry assemblies, or ultrasound transducers."
    elif "THEATRE" in model_upper:
        sys_type = "Surgical Suite & Anesthesia Infrastructure"
        deduction = "* Pneumatic Loop: Verify gas pressure mixers, trace breathing lines for leaks, and test flow sensors.\n* RF Output: Check electrosurgical Diathermy ESU modules for output voltage shifts."
    else:
        sys_type = "Advanced Clinical System"
        deduction = "* Core SMPS Check: Inspect power lines for stable 5V/12V/24V outputs and reset the logic registers."

    response = f"### INTELLIGENCE REPORT FOR: {machine_model.upper()}\n"
    response += f"**Classification Profile:** `{sys_type}` | **Target Malfunction Key:** `{query_keyword.upper()}`\n\n"

    if past_fixes:
        response += "### HIGH-PRIORITY: VERIFIED PAST FIELD SERVICE FIXES FOUND\n"
        for fix, date in past_fixes:
            clean_date = date.split("T")[0]
            response += f"* **Logged Remedy ({clean_date}):** *\"{fix}\"*\n"
        response += "\n---\n"

    if user_suggestion.strip():
        response += f"#### ACTIVE TEAM BRAINSTORMING INTERACTION\nObservation: *\"{user_suggestion}\"*\n\n"

    response += f"#### STEP-BY-STEP CORRECTIVE SERVICE PROTOCOL\n"
    if rows:
        for title, content in rows[:2]:
            response += f"1. **Via {title}:** Isolate modular circuitry loops and align parameters.\n"
    else:
        response += f"{deduction}\n"
        
    response += "3. **Alignment Sweep:** Flush paths, secure bus lines, and initialize home position."
    return response
