import os
import pandas as pd
from django.core.management.base import BaseCommand
from records.models import DiseaseRecord, Case
from dictionaries.models import ExposureDictionary, DiseaseDictionaryEntry, JobCodeOccupation
from django.conf import settings
from django.db import transaction

class Command(BaseCommand):
    help = 'Imports main data from basic_data.xlsx.'

    def handle(self, *args, **options):
        excel_file_path = os.path.join(settings.BASE_DIR, 'data', 'basic_data.xlsx')
        if not os.path.exists(excel_file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {excel_file_path}"))
            return

        self.stdout.write(f"Importing data from: {excel_file_path}")
        # 'ids' 컬럼은 문자열로 읽고, 빈 셀은 빈 문자열로 대체합니다.
        # 📝 Pandas가 숫자를 float으로 읽는 것을 방지하기 위해 dtype=str을 기본 적용합니다.
        df = pd.read_excel(excel_file_path, sheet_name='Sheet1', dtype=str).fillna('')

        self.stdout.write(self.style.WARNING("Deleting old DiseaseRecord data..."))
        DiseaseRecord.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Old DiseaseRecord data deleted."))

        valid_disease_names = {e.disease_name: e for e in DiseaseDictionaryEntry.objects.all()}
        valid_job_names = {j.occupation: j for j in JobCodeOccupation.objects.all()}
        valid_exposure_names = set(ExposureDictionary.objects.values_list('name', flat=True))

        if not valid_exposure_names:
            self.stdout.write(self.style.WARNING("Exposure dictionary is empty. Please run `import_exp_dic` first."))
        
        etc_exposure, created = ExposureDictionary.objects.get_or_create(name='기타')
        
        with transaction.atomic():
            created_count = 0
            for index, row in df.iterrows():
                if not row.get('fid'):
                    continue
                
                case_instance, _ = Case.objects.get_or_create(fid=row['fid'])

                # ▼▼▼▼▼ 노출 기간 데이터 정리 로직 수정 ▼▼▼▼▼
                # errors='coerce'를 사용하여 숫자가 아닌 값을 NaN으로 만들고, 
                # .dropna()와 비슷한 효과를 내도록 None으로 처리합니다.
                
                # 'exp_start' 정리
                exp_start_val = row.get('exp_start')
                exp_start_num = pd.to_numeric(exp_start_val, errors='coerce')
                exp_start_db = int(exp_start_num) if pd.notna(exp_start_num) else None
                
                # 'exp_period' 정리
                exp_period_val = row.get('exp_period')
                exp_period_num = pd.to_numeric(exp_period_val, errors='coerce')
                exp_period_db = int(exp_period_num) if pd.notna(exp_period_num) else None
                # ▲▲▲▲▲ 데이터 정리 로직 수정 완료 ▲▲▲▲▲
                
                # Raw 데이터
                disease_raw = str(row.get('disease', '')).strip()
                job_raw = str(row.get('job', '')).strip()
                exposure_raw = str(row.get('exposure', '')).strip()

                # 사전 연결 (ForeignKey)
                disease_dict_entry = valid_disease_names.get(disease_raw, None)
                job_dict_entry = valid_job_names.get(job_raw, None)
                
                # fname 필드를 우선적으로 사용, 없으면 fnames 사용
                fname_value = row.get('fname', '') or row.get('fnames', '')

                record = DiseaseRecord(
                    case=case_instance,
                    ids=row.get('ids', ''),
                    fnames=fname_value,  # fname 우선, fnames 대체

                    # --- 최종/사전 연결 필드 ---
                    disease=disease_dict_entry,
                    job=job_dict_entry,
                    disease_code=row.get('disease_code', ''),
                    job_code=row.get('job_code', ''),

                    # --- Raw/Original 필드 (초기 import시에는 현재 값과 동일) ---
                    original_disease_name=disease_raw,
                    original_disease_code=row.get('disease_code', ''),
                    original_job=job_raw,
                    original_job_code=row.get('job_code', ''),
                    original_exposure=exposure_raw,
                    original_decision=row.get('decision', ''),
                    original_smry=row.get('smry', ''),
                    original_pdf_link=row.get('pdf_link', ''),
                    original_pop_link=row.get('pop_link', ''),
                    original_process_link=row.get('process_link', ''),
                    original_exp_start=exp_start_db,
                    original_exp_period=exp_period_db,

                    # --- 기타 필드 ---
                    decision=row.get('decision', ''),
                    smry=row.get('smry', ''),
                    pdf_link=row.get('pdf_link', ''),
                    pop_link=row.get('pop_link', ''),
                    process_link=row.get('process_link', ''),
                    # 📝 정수형으로 정리된 값 할당
                    exp_start=exp_start_db,
                    exp_period=exp_period_db,
                )
                
                record.save()
                created_count += 1

                # ManyToManyField (exposure) 처리
                if exposure_raw:
                    exposure_items = [item.strip() for item in exposure_raw.split(',') if item.strip()]
                    exposures_to_link = []
                    for item_name in exposure_items:
                        try:
                            exposure_instance = ExposureDictionary.objects.get(name=item_name)
                            exposures_to_link.append(exposure_instance)
                        except ExposureDictionary.DoesNotExist:
                            exposures_to_link.append(etc_exposure)
                            
                    record.exposure.set(set(exposures_to_link))

        self.stdout.write(self.style.SUCCESS(f"Successfully imported {created_count} records."))
