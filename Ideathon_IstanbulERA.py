
"""
Yapay Zeka Teknoloji Akademisi Ideathon EDL çalışması Fer,Naz
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# --- ADIM 1: Veri Yükleme ve Ön İşleme ---
def prepare_data(file_path):
    df = pd.read_csv(file_path)
    
    # Burada boş değerleri temizledik (Özellikle yükseklik ve risk skoru kritik)
    df = df.dropna(subset=['Risk_Skoru', 'SAMPLE_yukseklik1', 'LATITUDE', 'LONGITUDE'])
    
    # Tarih ve saat verilerini işleyerek gün ve saat verilerini ortaya çıkardık.
    df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'])
    df['hour'] = df['DATE_TIME'].dt.hour
    df['day_of_week'] = df['DATE_TIME'].dt.dayofweek
    
    return df

# --- ADIM 2: Tahminleme Katmanı (AI Prediction) ---
def train_prediction_model(df):
    # Girdi özellikleri: Konum, Zaman, Hız ve Yükseklik
    features = ['LATITUDE', 'LONGITUDE', 'hour', 'day_of_week', 'AVERAGE_SPEED', 'SAMPLE_yukseklik1']
    X = df[features]
    y = df['Risk_Skoru']
    
    # Veriyi eğitim ve test olarak eğittik
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Model: Rastgele Orman (Random Forest) - Karmaşık ilişkileri yakalamakta iyidir
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    # Model başarısını ölç
    preds = model.predict(X_test)
    print(f"Model Tahmin Hatası (MAE): {mean_absolute_error(y_test, preds):.4f}")
    
    return model

# --- ADIM 3: Optimizasyon Katmanı (Smart Positioning) ---
def optimize_locations(df):
    # Geohash bazında gruplayarak bölgelerin karakteristliğini çıkardık.
    # Amacımız hem riskin yüksek olduğu hem de yokuşun zorladığı yerleri bulmak
    optimization_df = df.groupby(['GEOHASH', 'LATITUDE', 'LONGITUDE']).agg({
        'Risk_Skoru': ['mean', 'max'],
        'SAMPLE_yukseklik1': 'mean',
        'NUMBER_OF_VEHICLES': 'sum'
    }).reset_index()
    
    # Sütun isimlerini düzeltiyoruz
    optimization_df.columns = ['GEOHASH', 'LATITUDE', 'LONGITUDE', 'Avg_Risk', 'Max_Risk', 'Altitude', 'Total_Traffic']
    
    # --- KRİTİK FORMÜL: Öncelik Puanı ---
    # %60 Ortalama Risk + %20 Maksimum Risk (Zirve anlar) + %20 Topografik Zorluk
    max_alt = optimization_df['Altitude'].max()
    optimization_df['Priority_Score'] = (
        (optimization_df['Avg_Risk'] * 0.60) + 
        (optimization_df['Max_Risk'] * 0.20) + 
        ((optimization_df['Altitude'] / max_alt) * 0.20)
    )
    
    # Puanı en yüksek olan ilk 10 "Mikro-Müdahale" noktasını buluyoruz
    recommendations = optimization_df.sort_values(by='Priority_Score', ascending=False).head(10)
    
    return recommendations

# --- ANA ÇALIŞTIRICI ---
if __name__ == "__main__":
    # 1. Veriyi hazırlama noktası
    data = prepare_data('Risk_Skoru.csv')
    
    # 2. AI Modelini ataması (Gelecek tahminleri için)
    ai_model = train_prediction_model(data)
    
    # 3. Risk oranını best_spots'a atıyoruz
    best_spots = optimize_locations(data)
    
    print("\n--- İstanbul Emisyon Risk Analizi: Top 10 Sıcak Nokta ---")
    print(best_spots[['GEOHASH', 'LATITUDE', 'LONGITUDE', 'Priority_Score']])
    
    # Sonuçları CSV olarak kaydettik .
    best_spots.to_csv('Yatirim_Onerileri.csv', index=False)