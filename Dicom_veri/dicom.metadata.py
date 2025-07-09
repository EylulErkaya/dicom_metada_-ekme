import os
import pydicom
from pathlib import Path
import pandas as pd
from datetime import datetime

class DicomMetadataViewer:
    def __init__(self, root_directory):
        self.root_directory = Path(root_directory)
        self.dicom_files = []
        self.metadata_list = []
    
    def find_dicom_files(self):
        """Tüm alt klasörlerde DICOM dosyalarini bulur"""
        print(f"DICOM dosyalari araniyor: {self.root_directory}")
        
        for file_path in self.root_directory.rglob('*'):
            if file_path.is_file():
                try:
                    # Dosya uzantisi kontrolü (DICOM dosyalari genellikle .dcm uzantili)
                    if file_path.suffix.lower() in ['.dcm', '.dicom'] or file_path.suffix == '':
                        # DICOM dosyasi olup olmadiğini kontrol et
                        ds = pydicom.dcmread(str(file_path), stop_before_pixels=True)
                        self.dicom_files.append(file_path)
                        print(f"✓ DICOM dosyasi bulundu: {file_path}")
                except:
                    # DICOM dosyasi değilse sessizce geç
                    continue
        
        print(f"\nToplam {len(self.dicom_files)} DICOM dosyasi bulundu.\n")
    
    def extract_metadata(self, detailed=False):
        """DICOM dosyalarindan metadata çikarir"""
        if not self.dicom_files:
            print("Önce DICOM dosyalarini bulun (find_dicom_files() metodunu çağirin)")
            return
        
        print("Metadata çikariliyor...")
        
        for file_path in self.dicom_files:
            try:
                ds = pydicom.dcmread(str(file_path), stop_before_pixels=True)
                
                # StudyDate'i tarih formatına çevir
                raw_date = getattr(ds, 'StudyDate', 'N/A')
                try:
                    formatted_date_study = datetime.strptime(raw_date, "%Y%m%d").strftime("%Y-%m-%d") if raw_date != 'N/A' else 'N/A'
                except:
                    formatted_date_study = raw_date


                #patient_birth_date'i tarih formatına çevir
                birth_date= getattr(ds, 'PatientBirthDate', 'N/A')
                try:
                    formatted_date_birth= datetime.strptime(birth_date, "%Y%m%d").strftime("%Y-%m-%d") if birth_date != 'N/A' else 'N/A'
                except:
                    formatted_date_birth= birth_date

                # Temel metadata bilgileri
                metadata = {
                        'Dosya_Yolu': str(file_path),
                        'Dosya_Adi': file_path.name,
                        'Klasör': str(file_path.parent),
                        'Hasta_ID': getattr(ds, 'PatientID', 'N/A'),
                        'Hasta_Adi': getattr(ds, 'PatientName', 'N/A'),
                        'Modalite': getattr(ds, 'Modality', 'N/A'),
                        'Çalişma_Tarihi': formatted_date_study,  
                        'Hasta_dogum_tarihi': formatted_date_birth,
                        'Seri_Numarasi': getattr(ds, 'SeriesNumber', 'N/A'),
                        'Görüntü_Numarasi': getattr(ds, 'InstanceNumber', 'N/A'),
                        'Satir_Sayisi': getattr(ds, 'Rows', 'N/A'),
                        'Sütun_Sayisi': getattr(ds, 'Columns', 'N/A'),
                        'yas' : getattr(ds,'PatientAgey' ,' N/A' )
                }

                 
                if detailed:
                    # Detayli metadata
                    metadata.update({
                        'Çalişma_Açiklamasi': getattr(ds, 'StudyDescription', 'N/A'),
                        'Seri_Açiklamasi': getattr(ds, 'SeriesDescription', 'N/A'),
                        'Doktor': getattr(ds, 'ReferringPhysicianName', 'N/A'),
                        'Cihaz_Üreticisi': getattr(ds, 'Manufacturer', 'N/A'),
                        'Cihaz_Modeli': getattr(ds, 'ManufacturerModelName', 'N/A'),
                        'Pixel_Spacing': getattr(ds, 'PixelSpacing', 'N/A'),
                        'Slice_Thickness': getattr(ds, 'SliceThickness', 'N/A'),
                        'Çalişma_UID': getattr(ds, 'StudyInstanceUID', 'N/A'),
                        'Seri_UID': getattr(ds, 'SeriesInstanceUID', 'N/A')
                    })
                
                self.metadata_list.append(metadata)
                
            except Exception as e:
                print(f"Hata - {file_path}: {str(e)}")
        
        print(f"✓ {len(self.metadata_list)} dosyadan metadata çikarildi.\n")
    
    def display_metadata(self, limit=None):
        """Metadata'lari konsola yazdirir"""
        if not self.metadata_list:
            print("Metadata bulunamadi. Önce extract_metadata() metodunu çağirin.")
            return
        
        display_count = limit if limit else len(self.metadata_list)
        
        for i, metadata in enumerate(self.metadata_list[:display_count]):
            print(f"\n{'='*60}")
            print(f"DICOM Dosyasi {i+1}/{len(self.metadata_list)}")
            print(f"{'='*60}")
            
            for key, value in metadata.items():
                print(f"{key:20}: {value}")
        
        if limit and len(self.metadata_list) > limit:
            print(f"\n... ve {len(self.metadata_list) - limit} dosya daha")
    
    def save_to_csv(self, output_file='dicom_metadata.csv'):
        """Metadata'lari CSV dosyasina kaydeder"""
        if not self.metadata_list:
            print("Metadata bulunamadi. Önce extract_metadata() metodunu çağirin.")
            return
        
        df = pd.DataFrame(self.metadata_list)
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✓ Metadata CSV dosyasina kaydedildi: {output_file}")
    
    def get_summary(self):
        """Genel özet bilgilerini gösterir"""
        if not self.metadata_list:
            print("Metadata bulunamadi.")
            return
        
        df = pd.DataFrame(self.metadata_list)
        
        print("\n" + "="*50)
        print("DICOM METAData ÖZETİ")
        print("="*50)
        print(f"Toplam DICOM dosyasi: {len(self.metadata_list)}")
        print(f"Farkli hasta sayisi: {df['Hasta_ID'].nunique()}")
        print(f"Farkli modalite: {df['Modalite'].unique()}")
        print(f"Farkli çalişma tarihi: {df['Çalişma_Tarihi'].nunique()}")
        print("\nModalite dağilimi:")
        print(df['Modalite'].value_counts())

def main():
    # Kullanim örneği
    print("DICOM Metadata Görüntüleyici")
    print("=" * 40)
    
    # Klasör yolunu buraya yazin
    root_folder = "DicomImages"
    
    if not os.path.exists(root_folder):
        print("Belirtilen klasör bulunamadi!")
        return
    
    # Viewer nesnesi oluştur
    viewer = DicomMetadataViewer(root_folder)
    
    # DICOM dosyalarini bul
    viewer.find_dicom_files()
    
    if not viewer.dicom_files:
        print("Hiç DICOM dosyasi bulunamadi!")
        return
    
    # Metadata çikar (detailed=True daha fazla bilgi verir)
    detailed = input("Detayli metadata istiyorsaniz 'yes' yazin (y/n): ").lower() == 'yes'
    viewer.extract_metadata(detailed=detailed)
    
    # Sonuçlari göster
    print("\n1. Konsola yazdir")
    print("2. CSV'ye kaydet")
    print("3. Özet bilgileri göster")
    print("4. Hepsini yap")
    
    choice = input("\nSeçiminiz (1-4): ")
    
    if choice in ['1', '4']:
        limit = input("Kaç dosya gösterilsin? (hepsi için Enter): ")
        limit = int(limit) if limit.isdigit() else None
        viewer.display_metadata(limit=limit)
    
    if choice in ['2', '4']:
        filename = input("CSV dosya adi (varsayilan: dicom_metadata2.csv): ")
        filename = filename if filename else 'dicom_metadata.csv'
        viewer.save_to_csv(filename)
    
    if choice in ['3', '4']:
        viewer.get_summary()

if __name__ == "__main__":
    # Gerekli kütüphanelerin yüklü olup olmadiğini kontrol et
    try:
        import pydicom
        import pandas as pd
    except ImportError as e:
        print(f"Gerekli kütüphaneler yüklü değil: {e}")
        print("Şu komutlari çaliştirin:")
        print("pip install pydicom pandas")
        exit(1)
    
    main()