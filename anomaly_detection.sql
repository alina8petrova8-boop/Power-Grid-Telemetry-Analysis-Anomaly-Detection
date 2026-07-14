-- Предполагается, что данные лежат в таблице: telemetry_log (timestamp, sensor_id, current_a)

-- 1. Сначала заполняем пропущенные значения как простейшая интерполяция через COALESCE и LAG/LEAD
WITH CleanedData AS (
    SELECT 
        timestamp,
        sensor_id,
        COALESCE(
            current_a, 
            (LAG(current_a) OVER(PARTITION BY sensor_id ORDER BY timestamp) + 
             LEAD(current_a) OVER(PARTITION BY sensor_id ORDER BY timestamp)) / 2.0
        ) as current_clean
    FROM telemetry_log
),

-- 2. Вычисляем скользящее среднее и стандартное отклонение
RollingStats AS (
    SELECT 
        timestamp,
        sensor_id,
        current_clean,
        AVG(current_clean) OVER w AS rolling_mean,
        STDDEV(current_clean) OVER w AS rolling_std
    FROM CleanedData
    WINDOW w AS (PARTITION BY sensor_id ORDER BY timestamp ROWS BETWEEN 30 PRECEDING AND CURRENT ROW)
)

-- 3. Рассчитываем Z-score и фильтруем аномалии
SELECT 
    timestamp,
    sensor_id,
    current_clean,
    rolling_mean,
    -- NULLIF защищает от деления на ноль, если данные были константой
    (current_clean - rolling_mean) / NULLIF(rolling_std, 0) AS z_score
FROM RollingStats
WHERE ABS((current_clean - rolling_mean) / NULLIF(rolling_std, 0)) > 3.0
ORDER BY timestamp DESC;



