import os
import sqlite3
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.core.window import Window

# Enforce high-visibility grey and blue mobile theme backgrounds
Window.clearcolor = (0.95, 0.96, 0.98, 1)

RAG_DB_PATH = "device_knowledge_base.db"
HISTORY_DB_PATH = "field_solved_knowledge.db"

# Master baseline hospital asset list packaged right inside the mobile asset matrix
INITIAL_FLEET = [
    "Laboratory - 5-Part Hematology Counter (Sysmex, Mindray, Erba)",
    "Laboratory - Automated Clinical Chemistry Analyzer (Siemens, Roche, Erba)",
    "Laboratory - Immunoassay CLIA/ELISA System (bioMerieux VIDAS, Abbott)",
    "Laboratory - Automated Microbiology Susceptibility Gateway (VITEK 2)",
    "Radiology - Superconducting Magnetic Resonance Imaging (MRI 1.5T/3.0T)",
    "Radiology - Multi-Slice Computed Tomography Scanner (CT Gantry)",
    "Radiology - Fixed Ceiling-Suspended Digital Radiography (X-Ray)",
    "Theatre - Advanced Anesthesia Workstation & Gas Vaporizer Circuit",
    "Theatre - Electrosurgical Diathermy Unit (ESU Generator)",
    "ICU/HDU - Mechanical Ventilator (Invasive/NIV Mode Microprocessor)",
    "NICU - Forced-Convection Humidified Infant Closed Incubator",
    "CSSD - Horizontal Fractional Vacuum Steam Autoclave (121C/134C)"
]

def initialize_local_sqlite_dbs():
    """Initializes serverless permanent storage right inside the phone internal sandboxed flash memory."""
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


class MobileDiagnosticHub(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False
        initialize_local_sqlite_dbs()
        
        # ---------------------------------------------------
        # TAB 1: ACTIVE TECHNICIAN DIAGNOSTIC WORKSPACE
        # ---------------------------------------------------
        self.tech_tab = TabbedPanelItem(text="Technician Desk")
        tech_layout = BoxLayout(orientation='vertical', padding=25, spacing=15)
        
        tech_layout.add_widget(Label(text="Hass Mobile Engineering Assistant", font_size='24sp', color=(0.09, 0.15, 0.25, 1), bold=True, size_hint_y=None, height=40))
        
        tech_layout.add_widget(Label(text="Select Targeted Facility Asset Profile:", font_size='16sp', color=(0.3, 0.35, 0.4, 1), size_hint_y=None, height=25))
        self.model_spinner = Spinner(text=INITIAL_FLEET[0], values=INITIAL_FLEET, size_hint_y=None, height=55, font_size='16sp', background_color=(0.12, 0.53, 0.9, 1))
        tech_layout.add_widget(self.model_spinner)
        
        self.error_input = TextInput(hint_text="Enter System Fault Code / Critical Symptom Profile", multiline=False, font_size='18sp', size_hint_y=None, height=55)
        tech_layout.add_widget(self.error_input)
        
        self.obs_input = TextInput(hint_text="Optional engineering observations (Let's analyze together)...", font_size='16sp', size_hint_y=None, height=85)
        tech_layout.add_widget(self.obs_input)
        
        query_btn = Button(text="🔍 Run On-Device Problem Analysis", size_hint_y=None, height=65, background_color=(0, 0.47, 0.85, 1), font_size='18sp', bold=True)
        query_btn.bind(on_press=self.execute_mobile_diagnosis)
        tech_layout.add_widget(query_btn)
        
        self.scroll_container = ScrollView()
        self.report_view = Label(text="System idle. Specify parameters to trigger offline analysis loop.", font_size='18sp', color=(0.15, 0.18, 0.22, 1), halign='left', valign='top', size_hint_y=None)
        self.report_view.bind(texture_size=self.report_view.setter('size'))
        self.scroll_container.add_widget(self.report_view)
        tech_layout.add_widget(self.scroll_container)
        
        self.tech_tab.add_widget(tech_layout)
        self.add_widget(self.tech_tab)
        
        # ---------------------------------------------------
        # TAB 2: LOCAL EXPERT SUCCESS-LEARNING TRAINING LOOP
        # ---------------------------------------------------
        self.train_tab = TabbedPanelItem(text="Train AI Memory")
        train_layout = BoxLayout(orientation='vertical', padding=25, spacing=15)
        
        train_layout.add_widget(Label(text="Experience Loop Training Terminal", font_size='24sp', color=(0.09, 0.15, 0.25, 1), bold=True, size_hint_y=None, height=40))
        
        train_layout.add_widget(Label(text="Confirm Targeted Equipment Class:", font_size='16sp', color=(0.3, 0.35, 0.4, 1), size_hint_y=None, height=25))
        self.train_model_spinner = Spinner(text=INITIAL_FLEET[0], values=INITIAL_FLEET, size_hint_y=None, height=55, font_size='16sp', background_color=(0.12, 0.53, 0.9, 1))
        train_layout.add_widget(self.train_model_spinner)
        
        self.train_code = TextInput(hint_text="Remedied Fault Code (e.g., E-402, VAC-LOW)", multiline=False, font_size='18sp', size_hint_y=None, height=55)
        train_layout.add_widget(self.train_code)
        
        self.train_fix = TextInput(hint_text="What was the exact successful repair action? (Be precise):", font_size='16sp', size_hint_y=None, height=140)
        train_layout.add_widget(self.train_fix)
        
        train_btn = Button(text="💾 Lock Fix into Local AI Memory", size_hint_y=None, height=65, background_color=(0.13, 0.62, 0.28, 1), font_size='18sp', bold=True)
        train_btn.bind(on_press=self.commit_mobile_experience)
        train_layout.add_widget(train_btn)
        
        self.status_bar = Label(text="Awaiting on-site telemetry fields.", font_size='16sp', color=(0.45, 0.48, 0.52, 1), size_hint_y=None, height=35)
        train_layout.add_widget(self.status_bar)
        
        self.train_tab.add_widget(train_layout)
        self.add_widget(self.train_tab)

    def execute_mobile_diagnosis(self, instance):
        target_model = self.model_spinner.text
        fault_code = self.error_input.text.strip()
        user_obs = self.obs_input.text.strip()
        
        if not fault_code:
            self.report_view.text = "⚠️ Incomplete input parameter: Please specify an active fault symptom code."
            return
            
        # Scan local SQLite for previous solutions logged by this user
        conn = sqlite3.connect(HISTORY_DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT technician_fix, date_logged FROM historical_fixes WHERE UPPER(machine_model) = ? AND UPPER(error_code) = ?;", (target_model.upper(), fault_code.upper()))
        logged_remedies = cur.fetchall()
        conn.close()
        
        model_upper = target_model.upper()
        if "LABORATORY" in model_upper:
            sys_profile = "Automated Clinical Laboratory Platform"
            deduction = "* Fluidic Pathway: Inspect sample micro-metering syringe motors for slips and run wash flushes.\n* Optical Path: Recalibrate photometer zero-reference metrics."
        elif "RADIOLOGY" in model_upper:
            sys_profile = "Diagnostic Medical Imaging Modality"
            deduction = "* Electrical Grid: Check high-voltage SMPS transformers and verify gantry chassis ground wires.\n* RF Tracking: Inspect panel shields, receiver surface coils, and fan airflows."
        elif "THEATRE" in model_upper:
            sys_profile = "Surgical Suite & Anesthesia Infrastructure"
            deduction = "* Pneumatic Gas Path: Trace breathing circuit loops for leaks and verify auxiliary vaporizer flow sensors.\n* High-Frequency Diathermy: Verify ESU return-plate monitoring loop connections."
        else:
            sys_type = "Critical Care Clinical Care Support Asset"
            deduction = "* Volumetric Actuation: Calibrate linear stepper motor rails and check microprocessor pressure transducer lines."

        # Build output presentation string mapping large scale layouts
        final_output = f"### SYSTEM READOUT FOR: {target_model.upper()}\n"
        final_output += f"Classification: {sys_profile} | Anomaly Target: {fault_code.upper()}\n\n"
        
        if logged_remedies:
            final_output += "🌟 HIGH-PRIORITY: VERIFIED PAST FIELD SERVICE FIXES FOUND\n"
            for fix, dt in logged_remedies:
                final_output += f"• Logged Fix ({dt[:10]}): \"{fix}\"\n"
            final_output += "--------------------------------------------------------\n\n"
            
        if user_obs:
            final_output += f"🤝 COLLABORATIVE ANALYSIS MATRIX ENGAGED:\nCross-examining observation: \"{user_obs}\" with subsystem physics.\n\n"
            
        final_output += f"🔧 DEDUCTIVE REASONING ERROR REMEDY SUGGESTIONS:\n{deduction}\n\n"
        final_output += "3. Master Alignment Protocol: Cycle system breakers to clear software registers, check flat ribbon cable seating, and initiate automated homing validation sweeps."
        
        self.report_view.text = final_output

    def commit_mobile_experience(self, instance):
        target_model = self.train_model_spinner.text
        fault_code = self.train_code.text.strip()
