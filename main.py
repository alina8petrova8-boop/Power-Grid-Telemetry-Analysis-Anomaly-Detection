mport pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def generate_telemetry_data(n_samples=1000):
    """Генерирует синтетические данные телеметрии энергосети с аномалиями и пропусками."""
    np.random.seed(42)
    time_index = pd.date_range(start="2026-07-13", periods=n_samples, freq="1min")
    
    # Базовые значения: Напряжение 220В, Ток 10А, Частота 50Гц
    voltage = np.random.normal(220, 1.5, n_samples)
    current = np.random.normal(10, 0.5, n_samples)
    frequency = np.random.normal(50, 0.02, n_samples)
    
    # 1. Имитация потери пакетов (пропуски данных)
    current[150:155] = np.nan
    voltage[150:155] = np.nan
    
    # 2. Имитация аномалий (переходные процессы, короткое замыкание, просадка сети)
    voltage[300:305] = 180.0          # Резкая просадка напряжения
    current[600:610] = np.random.normal(35, 2, 10)  # Резкий скачок тока (перегрузка)
    frequency[800] = 49.2             # Провал частоты
    
    return pd.DataFrame({
        'timestamp': time_index,
        'voltage_v': voltage,
        'current_a': current,
        'frequency_hz': frequency
    })

def process_and_detect_anomalies(df, window_size=30, threshold=3):
    """Очищает данные и находит аномалии с помощью Z-score на скользящем окне."""
    # Создаем копию, чтобы не менять исходный датафрейм
    processed_df = df.copy()
    
    # Очистка данных: линейная интерполяция для заполнения пропусков (NaN)
    for col in ['voltage_v', 'current_a', 'frequency_hz']:
        processed_df[f'{col}_clean'] = processed_df[col].interpolate(method='linear')
        
        # Расчет скользящих метрик
        rolling_mean = processed_df[f'{col}_clean'].rolling(window=window_size, min_periods=1).mean()
        rolling_std = processed_df[f'{col}_clean'].rolling(window=window_size, min_periods=1).std().fillna(0)
        
        # Расчет Z-score с защитой от деления на ноль
        z_score = (processed_df[f'{col}_clean'] - rolling_mean) / (rolling_std + 1e-9)
        
        # Флаг аномалии
        processed_df[f'{col}_anomaly'] = z_score.abs() > threshold
        
    return processed_df

def visualize_data(df):
    """Строит интерактивный дашборд с помощью Plotly."""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        subplot_titles=("Телеметрия Тока (Амперы) и поиск перегрузок", 
                                        "Телеметрия Напряжения (Вольты)"))

    # График тока
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['current_a_clean'], 
                             mode='lines', name='Ток (Очищенный)', line=dict(color='blue')), row=1, col=1)
    
    # Выделяем аномалии тока красными точками
    anomalies_current = df[df['current_a_anomaly']]
    fig.add_trace(go.Scatter(x=anomalies_current['timestamp'], y=anomalies_current['current_a_clean'], 
                             mode='markers', name='Аномалия Тока', 
                             marker=dict(color='red', size=8, symbol='x')), row=1, col=1)

    # График напряжения
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['voltage_v_clean'], 
                             mode='lines', name='Напряжение (Очищенное)', line=dict(color='green')), row=2, col=1)
    
    anomalies_voltage = df[df['voltage_v_anomaly']]
    fig.add_trace(go.Scatter(x=anomalies_voltage['timestamp'], y=anomalies_voltage['voltage_v_clean'], 
                             mode='markers', name='Аномалия Напряжения', 
                             marker=dict(color='red', size=8, symbol='x')), row=2, col=1)

    fig.update_layout(height=700, title_text="Дашборд анализа стабильности энергосети", template="plotly_white")
    
    # Сохраняем интерактивный график в HTML
    fig.write_html("dashboard.html")
    print("Дашборд успешно сгенерирован: dashboard.html")

if __name__ == "__main__":
    print("1. Генерация сырых данных телеметрии...")
    raw_data = generate_telemetry_data()
    
    print("2. Обработка данных (ETL) и поиск аномалий...")
    analyzed_data = process_and_detect_anomalies(raw_data)
    
    print("3.Построение визуализации...")
    visualize_data(analyzed_data)
