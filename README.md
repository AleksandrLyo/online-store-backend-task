# Приложение периодически загружающее данные из стороннего API и обновляющее их в БД

## Фичи
- Периодическая синхронизация с внешним API
- База данных PostgreSQL
- Эндпоинт для получения данных

## Пример
<img width="1174" height="385" alt="image" src="https://github.com/user-attachments/assets/7829e344-91d4-419b-9014-190a1adc3a99" />


## Установка
1. Скопировать и настроить `.env.example` в `.env`
2. Запустить: `docker-compose up --build`
3. Эндпоинт для получения данных: `http://localhost:5555/info`
