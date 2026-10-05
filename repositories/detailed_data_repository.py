import pandas as pd
from database_connector import DatabaseConnector
from repositories.medication_repository import MedicationRepository

class DetailedDataRepository:
    def __init__(self, db_connector: DatabaseConnector):
        self.db_connector = db_connector
        self.medication_repo = MedicationRepository(db_connector) 

    def get_detailed_data_for_visit(self, patient_id, visit_date):
        print(f"Detaylı veriler çekiliyor: Hasta ID: {patient_id}, Ziyaret Tarihi: {visit_date}")
        detailed_data = {}
        try:
            # Ziyaret ID'sini çekme ve ziyarete özel verileri alma
            visit_id_query = f"SELECT VisitID FROM Visits WHERE PatientID = {patient_id} AND VisitDate = '{visit_date}'"
            visit_id_df = pd.read_sql_query(visit_id_query, self.db_connector.get_connection())
            
            if not visit_id_df.empty:
                visit_id = visit_id_df.iloc[0]['VisitID']
                
                detailed_data['Vital Bulgular'] = self.get_vital_signs(visit_id)
                detailed_data['Kan Testi'] = self.get_blood_tests(visit_id)
                detailed_data['Genetik Biyobelirteçler'] = self.get_genetic_markers(visit_id)
                detailed_data['Görüntü Analizleri'] = self.get_image_analyses(visit_id) # The key is 'Görüntü Analizleri'
            
            # Klinik değerlendirmeler ve ilaç verileri ziyaretten bağımsızdır.
            detailed_data['Klinik Değerlendirmeler'] = self.get_clinical_evaluations(patient_id)
            
            # Tüm tedavi şemalarını çekme
            regimens_df = self.medication_repo.get_patient_regimens(patient_id)

            detailed_data['Tedavi Şemaları'] = regimens_df
            
            # Tüm doz ayarlamalarını çekme (eğer tedavi şeması varsa)
            if not regimens_df.empty:
                all_adjustments = []
                for regimen_id in regimens_df['RegimenID']:
                    adjustments = self.medication_repo.get_regimen_adjustments(regimen_id)
                    if not adjustments.empty:
                        all_adjustments.append(adjustments)
                
                if all_adjustments:
                    detailed_data['Doz Ayarlamaları'] = pd.concat(all_adjustments, ignore_index=True)
                else:
                    detailed_data['Doz Ayarlamaları'] = pd.DataFrame()
            else:
                detailed_data['Doz Ayarlamaları'] = pd.DataFrame()

        

        except Exception as e:
            print(f"Hata: Detaylı veriler çekilirken bir sorun oluştu: {e}")
            
        return detailed_data
    
    def get_vital_signs(self, visit_id):
        """Belirli bir ziyaretin vital bulgularını çeker."""
        vital_signs_query = f"""
        SELECT TestName, Value, Unit FROM VitalSigns 
        WHERE VisitID = {visit_id}
        """
        return pd.read_sql_query(vital_signs_query, self.db_connector.get_connection())

    def get_blood_tests(self, visit_id):
        """Belirli bir ziyaretin kan testi sonuçlarını çeker."""
        blood_tests_query = f"""
        SELECT btl.TestName, bt.Value, bt.ReferenceRange, bt.Status
        FROM BloodTests bt
        JOIN BloodTestList btl ON bt.BloodTestListID = btl.BloodTestListID
        WHERE bt.VisitID = {visit_id}
        """
        df = pd.read_sql_query(blood_tests_query, self.db_connector.get_connection())
        df.rename(columns={'TestName': 'Test Adı'}, inplace=True)
        return df

    def get_genetic_markers(self, visit_id):
        """Belirli bir ziyaretin genetik biyobelirteçlerini çeker."""
        genetic_markers_query = f"""
        SELECT gml.MarkerName, gm.Percentage, gm.Result, gm.TargetedTherapy
        FROM GeneticMarkers gm
        JOIN GeneticMarkersList gml ON gm.MarkerListID = gml.MarkerListID
        WHERE gm.VisitID = {visit_id}
        """
        df = pd.read_sql_query(genetic_markers_query, self.db_connector.get_connection())
        df.rename(columns={'MarkerName': 'Biyobelirteç'}, inplace=True)
        return df
    
    def get_clinical_evaluations(self, patient_id):
        """Belirli bir hastaya ait klinik değerlendirme verilerini çeker."""
        clinical_eval_query = f"""
        SELECT ce.SmokingStatus, ce.FamilyHistory, ce.PerformanceStatus, ce.Comorbidities, ce.ECOG_Score
        FROM Clinical_Evaluations ce
        WHERE ce.PatientID = {patient_id}
        """
        return pd.read_sql_query(clinical_eval_query, self.db_connector.get_connection())
    
    def get_image_analyses(self, visit_id):
        """Belirli bir ziyaretin görüntü analizi verilerini çeker."""
        image_analyses_query = f"""
        SELECT
            image_analysis_id,
            sketchfab_model_url,
            sketchfab_model_id,
            diagnosis_notes
        FROM
            ImageAnalyses
        WHERE
            visit_id = {visit_id}
        """
        return pd.read_sql_query(image_analyses_query, self.db_connector.get_connection())
    # repositories/detailed_data_repository.py (Güncellenmiş Kısım)

    def get_all_blood_tests_for_patient(self, patient_id):
        """Belirli bir hastanın tüm ziyaretlerine ait kan testi sonuçlarını çeker."""
        blood_tests_query = f"""
        SELECT
            btl.TestName AS 'Test Adı',
            bt.Value AS 'Sonuç',
            bt.ReferenceRange AS 'Referans aralığı',
            v.VisitDate AS 'Tarih'
        FROM
            BloodTests bt
        JOIN
            BloodTestList btl ON bt.BloodTestListID = btl.BloodTestListID
        JOIN
            Visits v ON bt.VisitID = v.VisitID
        WHERE
            v.PatientID = {patient_id}
        ORDER BY
            v.VisitDate ASC
        """
        df = pd.read_sql_query(blood_tests_query, self.db_connector.get_connection())
        return df
    
    def get_all_genetic_markers_for_patient(self, patient_id):
        """Belirli bir hastanın tüm ziyaretlerine ait genetik biyobelirteç sonuçlarını çeker."""
        genetic_query = f"""
        SELECT
            gml.MarkerName AS 'Biyobelirteç',
            gm.Result AS 'Sonuç',
            gm.Percentage AS 'Değer',
            v.VisitDate AS 'Tarih'
        FROM
            GeneticMarkers gm
        JOIN
            GeneticMarkersList gml ON gm.MarkerListID = gml.MarkerListID
        JOIN
            Visits v ON gm.VisitID = v.VisitID
        WHERE
            v.PatientID = {patient_id}
        ORDER BY
            v.VisitDate ASC
        """
        df = pd.read_sql_query(genetic_query, self.db_connector.get_connection())
        return df