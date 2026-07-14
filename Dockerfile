# Используем официальный легкий образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями (создай файл requirements.txt с содержимым: pandas numpy plotly)
COPY requirements.txt .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY main.py .

# Указываем команду для запуска скрипта
CMD ["python", "main.py"]




