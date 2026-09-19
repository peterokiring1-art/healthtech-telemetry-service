import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian
import numpy as np
import os

def create_mock_dicom_file(filename="raw_patient_scan.dcm"):
    """
    Synthesizes a true clinical DICOM standard file wrapper on disk,
    complete with private client metadata and a mock raw image array.
    """
    # 1. Establish necessary DICOM File Meta Header parameters
    file_meta = FileMetaDataset()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2' # CT Image Storage UID
    file_meta.MediaStorageSOPInstanceUID = '1.2.3.4.5.6.7'
    file_meta.ImplementationClassUID = '1.2.3.4.5.6.8'

    ds = Dataset()
    ds.file_meta = file_meta
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    # 2. Inject Patient Protected Health Information (PHI)
    ds.PatientName = "Doe^John^Clinical"
    ds.PatientID = "PT-994827-X"
    ds.PatientBirthDate = "19780514"
    ds.PatientSex = "M"
    ds.StudyInstanceUID = "1.2.840.113619.2.55.3"
    ds.SeriesInstanceUID = "1.2.840.113619.2.55.3.4"
    ds.SOPInstanceUID = "1.2.3.4.5.6.7"
    ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.2'

    # 3. Add Spatial Matrix Dimensions 
    ds.Rows = 128
    ds.Columns = 128
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"

    # 4. Generate mock monochrome pixel matrix (e.g., center organ simulation)
    pixel_array = np.zeros((128, 128), dtype=np.uint16)
    rr, cc = np.ogrid[:128, :128]
    center_organ_mask = (rr - 64)**2 + (cc - 64)**2 < 40**2
    pixel_array[center_organ_mask] = 800  # Elevated density pixel marker
    
    # Pack raw binary bytes directly into the standard element tag mapping
    ds.PixelData = pixel_array.tobytes()

    ds.save_as(filename, write_like_original=False)
    print(f"📦 Mock clinical file generated successfully: '{filename}'")

def anonymize_and_extract_dicom(input_filename, output_filename):
    """
    Parses a target DICOM structure, completely strips out private metadata
    to ensure compliance, and extracts clean raw matrix dimensions.
    """
    # Load file using the native pydicom reader engine
    ds = pydicom.dcmread(input_filename)
    
    print("\n🔍 EXTRANEOUS HEALTH METADATA PRE-ANONYMIZATION:")
    print(f" -> Patient Name Attribute: {getattr(ds, 'PatientName', 'Not Found')}")
    print(f" -> Patient ID Attribute: {getattr(ds, 'PatientID', 'Not Found')}")
    print(f" -> Patient Birth Date: {getattr(ds, 'PatientBirthDate', 'Not Found')}")

    # --- Systematic Anonymization Action Block ---
    # Define internal mapping callback to intercept and clear custom naming tags
    def clear_patient_names(dataset, element):
        if element.VR == "PN":  # VR 'PN' denotes Person Name string tags
            element.value = "ANONYMOUS^PATIENT"

    # Walk the element tree recursively to wipe out any nested identity tags
    ds.walk(clear_patient_names)

    # Clean target attributes cleanly or replace with placeholder trackers
    ds.PatientID = "ANON-PROJ-PHASE2"
    
    if "PatientBirthDate" in ds:
        ds.PatientBirthDate = ""  # Zero-out dates to strip age profiling vectors
        
    # Remove hidden private vendor tags completely
    ds.remove_private_tags()

    # Save the updated data structure back to disk safely
    ds.save_as(output_filename)
    print(f"\n🔒 De-identified structure exported to: '{output_filename}'")

    # --- Raw Matrix Data Extraction ---
    # Access pixel data directly through the built-in numpy image handler array
    extracted_matrix = ds.pixel_array
    
    print("\n📊 EXTRACTED DATA MATRIX DIAGNOSTICS:")
    print(f" -> Raw Numpy Target Matrix Shape: {extracted_matrix.shape}")
    print(f" -> Array Element Data Type: {extracted_matrix.dtype}")
    print(f" -> Maximum Signal Amplitude inside Matrix: {extracted_matrix.max()}")

if __name__ == "__main__":
    raw_file = "raw_patient_scan.dcm"
    clean_file = "anonymized_patient_scan.dcm"
    
    # Run pipeline
    create_mock_dicom_file(raw_file)
    anonymize_and_extract_dicom(raw_file, clean_file)
    
    # Cleanup files locally
    for f in [raw_file, clean_file]:
        if os.path.exists(f):
            os.remove(f)
