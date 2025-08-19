Мини-движок 2D на Pygame

Запуск:

1) Установите зависимости:

```bash
python -m pip install -r requirements.txt
```

2) Запустите пример:

```bash
python main.py
```

Управление: стрелки или WASD. Закрыть окно — крестик.

Если вы запускаете на сервере/в CI без дисплея (Linux), можно использовать «головной» режим:

```bash
SDL_VIDEODRIVER=dummy python main.py
```