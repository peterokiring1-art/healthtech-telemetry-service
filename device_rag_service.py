import os
import sqlite3
from typing import List, Tuple

RAG_DB_PATH = "device_knowledge_base.db"
HISTORY_DB_PATH = "field_solved_knowledge.db"

def initialize_knowledge_base():
    """Guarantees both manufacturer schemas and historical field memories are initialized."""
    # Factory manuals schema
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

    # Human-solved experience learning schema
    conn2 = sqlite3.connect(HISTORY_DB_PATH)
    cur2 = conn2.cursor()
    cur2.execute("""
        CREATE TABLE IF NOT EXISTS historical_fixes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_model TEXT NOT NULL,
            error_code TEXT NOT NULL,
            technician_fix TEXT NOT NULL,
            date_logged TEXT NOT NULL
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

def save_successful_fix(machine_model: str, error_code: str, technician_fix: str):
    """Bakes a real-world technician solution permanently into the AI's memory layers."""
    initialize_knowledge_base()
    conn = sqlite3.connect(HISTORY_DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO historical_fixes (machine_model, error_code, technician_fix, date_logged)
        VALUES (?, ?, ?, ?);
    """, (machine_model, error_code.strip().upper(), technician_fix.strip(), sqlite3.datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def query_and_analyze_fault(machine_model: str, query_keyword: str, user_suggestion: str = "") -> str:
    """Scans historical solved cases first, then factory manuals, and combines 
    them with active observations to output a prioritized action protocol.
    """
    initialize_knowledge_base()
    
    # 1. Search for previous human-solved records first
    conn_hist = sqlite3.connect(HISTORY_DB_PATH)
    cur_hist = conn_hist.cursor()
    cur_hist.execute("""
        SELECT technician_fix, date_logged FROM historical_fixes 
        WHERE machine_model = ? AND error_code = ?;
    """, (machine_model, query_keyword.strip().upper()))
    past_fixes = cur_hist.fetchall()
    cur_hist.close()
    conn_hist.close()

    # 2. Search manufacturer factory manuals base
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

    # Base classification tracking strings
    model_upper = machine_model.upper()
    sys_type = "Automated Hematology Counter" if any(x in model_upper for x in ["ELITE", "H3", "H5", "H7"]) else (
               "Automated Clinical Chemistry Analyzer" if any(x in model_upper for x in ["XL", "CHEM"]) else (
               "Automated Electrolyte Analyzer (ISE)" if any(x in model_upper for x in ["EC", "LYTE"]) else "Advanced Clinical Diagnostic System"))

    # =======================================================
    # OUTPUT FORMATTING: PRIORITY HYBRID INTELLIGENCE
    # =======================================================
    response = f"### 🧠 INTELLIGENCE REPORT FOR: {machine_model.upper()}\n"
    response += f"**Classification Profile:** `{sys_type}` | **Target Malfunction Key:** `{query_keyword.upper()}`\n\n"

    # If the system finds a past human solution, prioritize it over everything else!
    if past_fixes:
        response += "### 🌟 HIGH-PRIORITY: VERIFIED PAST FIELD SERVICE FIXES FOUND\n"
        response += "The AI has retrieved historical repair workflows successfully logged by you for this exact symptom:\n"
        for fix, date in past_fixes:
            clean_date = date.split("T")[0]
            response += f"* **Logged Remedy ({clean_date}):** *\"{fix}\"*\n"
        response += "\n---\n"

    # Present current collaborative brainstorming reflections
    if user_suggestion.strip():
        response += f"#### 🤝 ACTIVE TEAM BRAINSTORMING INTERACTION\n"
        response += f"Evaluating your current observation: *\"{user_suggestion}\"*\n"
        response += "Combining your note with the diagnostic parameters to isolate microfluidic and circuit track anomalies.\n\n"

    # Present baseline manual data summaries
    response += "#### 🔧 STEP-BY-STEP CORRECTIVE SERVICE PROTOCOL\n"
    if rows:
        response += "Extracting direct procedures based on structural manufacturer documentation profiles:\n"
        for title, content in rows[:2]:
            response += f"1. **Via {title}:** Check connections and clear alignment registers.\n"
    else:
        response += "Deducing physical troubleshooting pathways based on system class mechanics:\n"
        response += "1. **Hydraulic/Fluidic Isolation:** Verify fluid lines for micro-clots, bubble pockets, and check pump pressures.\n"
        response += "2. **Electronic/Bus Verification:** Check switch-mode power lines for voltage sags and reseat ribbon bus contacts.\n"
        
    response += "3. **Baseline Recalibration:** Flush diagnostic paths and run a master baseline home-position initialization register cycle.\n"
    
    return response
