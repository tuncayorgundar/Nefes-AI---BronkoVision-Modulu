import pandas as pd
from database_connector import DatabaseConnector

class MedicationRepository:
    def __init__(self, db_connector: DatabaseConnector):
        self.db_connector = db_connector

    def get_patient_regimens(self, patient_id):
        """
        Belirli bir hasta için tüm tedavi şemalarını çeker.
        """
        query = f"""
        SELECT RegimenID, RegimenName, StartDate, EndDate, ProtocolDescription, CurrentStatus
        FROM TreatmentRegimens
        WHERE PatientID = {patient_id}
        ORDER BY StartDate DESC
        """
        return pd.read_sql_query(query, self.db_connector.get_connection())

    def get_regimen_adjustments(self, regimen_id):
        """
        Belirli bir tedavi şeması için tüm doz ayarlamalarını çeker.
        """
        query = f"""
        SELECT AdjustmentID, CycleNumber, AdjustmentDate, MedicationName, 
               OriginalDose_mg_per_m2, AdjustedDose_mg_per_m2, 
               AdjustmentReason, Symptom, LabResults, ECOG_PerformanceStatus
        FROM DoseAdjustments
        WHERE RegimenID = {regimen_id}
        ORDER BY CycleNumber DESC
        """
        return pd.read_sql_query(query, self.db_connector.get_connection())