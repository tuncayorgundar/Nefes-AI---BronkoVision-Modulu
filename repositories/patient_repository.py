import pandas as pd
from database_connector import DatabaseConnector
from models.patient import Patient
from datetime import datetime

class PatientRepository:
    def __init__(self, db_connector: DatabaseConnector):
        self.db_connector = db_connector

    def get_all_patients(self):
        """
        Veritabanındaki tüm hastaların temel bilgilerini ve ziyaret tarihlerini çeker.
        """
        all_patients = []
        try:
            # Hastaların temel bilgilerini çek
            patients_query = """
            SELECT PatientID, FirstName, LastName, DateOfBirth, Gender, BloodType, PhoneNumber, Address, Status
            FROM Patients;
            """
            df_patients = pd.read_sql_query(patients_query, self.db_connector.get_connection())

            # Hastaların ziyaret tarihlerini çek
            visits_query = "SELECT PatientID, VisitDate FROM Visits ORDER BY VisitDate;"
            df_visits = pd.read_sql_query(visits_query, self.db_connector.get_connection())

            if not df_patients.empty:
                for index, row in df_patients.iterrows():
                    patient_id = row['PatientID']
                    
                    # Her hasta için ziyaret tarihlerini filtrele
                    patient_visits = df_visits[df_visits['PatientID'] == patient_id]['VisitDate']
                    visit_dates = [datetime.strptime(str(d).split(' ')[0], '%Y-%m-%d') for d in patient_visits.tolist()]
                    
                    # Patient nesnesini oluştur
                    patient = Patient(
                        patient_id=row['PatientID'],
                        first_name=row['FirstName'],
                        last_name=row['LastName'],
                        date_of_birth=row['DateOfBirth'],
                        gender=row['Gender'],
                        blood_type=row['BloodType'],
                        phone_number=row['PhoneNumber'],
                        address=row['Address'],
                        status=row['Status'],
                        visit_dates=visit_dates
                    )
                    all_patients.append(patient)
            
        except Exception as e:
            print(f"Hata: Hastalar çekilirken bir sorun oluştu: {e}")
        
        return all_patients

    def get_patient_by_id(self, patient_id):
        """
        Belirli bir hasta ID'sine göre hasta nesnesini döndürür.
        """
        all_patients = self.get_all_patients()
        for patient in all_patients:
            if patient.patient_id == patient_id:
                return patient
        return None