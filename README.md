# ᓭ⍑ᒷꖎꖎ ᒲᔑ⊣╎ᓵ <sup>[1](#footnote-1)</sup>

![Preview](./assets/preview.png)

Автоматизированная система управления dotfiles с поддержкой strap-файлов, управления cron заданиями и синхронизации.

## Установка

Запустите скрипт bootstrap для настройки dotfiles:

```bash
python3 bootstrap.py
```

Скрипт автоматически:

- Обрабатывает все `.strap` файлы в репозитории
- Создает символические ссылки и копирует файлы согласно конфигурации
- Устанавливает cron задания (на macOS и Linux)

## Управление dotfiles

### Команда `deytefiles`

Основной управляющий скрипт для работы с dotfiles репозиторием.

#### Bootstrap - Инициализация dotfiles

```bash
deytefiles bootstrap    # Запустить процесс установки
deytefiles bootstrap -q # Без уведомлений
```

Команда `bootstrap` выполняет:

1. Запуск `bootstrap.py` из корня репозитория
2. Обработку всех `.strap` файлов
3. Создание символических ссылок и копирование файлов
4. Применение cron заданий
5. Отправку уведомления о результате

#### Sync - Синхронизация с удаленным репозиторием

```bash
deytefiles sync              # Автоматическая синхронизация
deytefiles sync -m "message" # С пользовательским сообщением коммита
deytefiles sync -f           # Принудительная отправка (--force-with-lease)
deytefiles sync -q           # Без уведомлений
```

Команда `sync` выполняет:

1. Добавление всех изменений в индекс (`git add -A`)
2. Создание коммита с меткой времени
3. Pull с rebase от origin
4. Push изменений
5. Отправку нативных уведомлений (macOS/Linux)

## Конфигурация `.strap` файлов

Каждый `.strap` файл в репозитории определяет конфигурацию для своего компонента:

```python
import os
from dotfiles import utils

strap_dir = os.path.dirname(__file__)

config = {
    'name': 'component-name',

    # Символические ссылки
    'link': [
        [source_path, target_path, utils.PLATFORM_ANY],
    ],

    # Копирование файлов
    'copy': [
        [source_path, target_path, utils.PLATFORM_DARWIN],
    ],

    # Cron задания (опционально)
    'cron': [
        ['0 * * * *', '/path/to/script.sh', utils.PLATFORM_LINUX],
    ]
}

utils.process_config(config)
```

### Платформы

- `utils.PLATFORM_ANY` - любая платформа
- `utils.PLATFORM_DARWIN` - только macOS
- `utils.PLATFORM_LINUX` - только Linux

### Управление Cron заданиями

Система автоматически управляет cron заданиями через выделенную секцию в crontab:

```
# BEGIN DEYTENIT DOTFILES STRAP CRON
0 * * * * /path/to/script.sh
*/30 * * * * /usr/local/bin/backup.py
# END DEYTENIT DOTFILES STRAP CRON
```

Особенности:

- Валидация cron выражений перед применением
- Автоматический rollback при ошибках
- Резервное копирование существующего crontab
- Поддержка только macOS и Linux

## Структура репозитория

```
.dotfiles/
├── bootstrap.py           # Основной скрипт установки
├── .strap                 # Корневой конфигурационный файл
├── .config/              # Конфигурации приложений
│   └── */
│       └── .strap        # Конфигурация для каждого приложения
├── .local/
│   ├── bin/
│   │   └── deytefiles    # Управляющий скрипт
│   └── share/
│       └── dotfiles/
│           └── utils.py  # Утилиты для обработки конфигураций
└── README.md
```

## Уведомления

Система использует нативные уведомления ОС:

- **macOS**: через `osascript` (AppleScript)
- **Linux**: через `notify-send` (dunst, mako, notification-daemon и др.)

## Footnotes

- <a name="footnote=1">[1]</a>: eng. Shell Magic _(Standard Galactic Alphabet)_
