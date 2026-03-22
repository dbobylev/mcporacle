## mcporacle

Локальный MCP server для Roo Code, который подключается к Oracle DB и возвращает ограниченный набор метаданных через безопасные MCP tools.

## Что уже реализовано

- Python-проект с установкой через `pip`
- MCP server со `stdio` transport
- Tool `get_table_info(schema_name, table_name)`
- Подключение к Oracle через переменные окружения
- Получение описания таблицы и колонок через анонимный PL/SQL-блок
- Базовая валидация входных параметров и обработка ошибок
- Минимальные unit-тесты на валидацию и формат ответа

## Стек

- Python 3.11+
- `oracledb`
- `mcp`

## Ограничения и безопасность

- Сервер рассчитан на запуск на Windows-хосте без Docker.
- Произвольные SQL-запросы от пользователя не поддерживаются.
- Tool работает только с фиксированной логикой на стороне сервера.
- `schema_name` и `table_name` проходят строгую валидацию как простые Oracle identifiers.
- Метаданные читаются только из `DBA_TABLES`, `DBA_TAB_COMMENTS`, `DBA_TAB_COLUMNS`, `DBA_COL_COMMENTS`.

## Структура проекта

```text
.
├── .env.example
├── pyproject.toml
├── readme.md
├── src/
│   └── mcporacle/
│       ├── config.py
│       ├── errors.py
│       ├── models.py
│       ├── server.py
│       ├── validation.py
│       ├── oracle/
│       │   └── client.py
│       └── services/
│           └── table_info.py
└── tests/
```

## Установка

### PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
```

## Настройка `.env`

Создайте `.env` на основе `.env.example`:

```dotenv
MCPORACLE_ORACLE_USER=system
MCPORACLE_ORACLE_PASSWORD=oracle
MCPORACLE_ORACLE_DSN=localhost:1521/FREEPDB1
MCPORACLE_LOG_LEVEL=INFO
```

Обязательные переменные:

- `MCPORACLE_ORACLE_USER`
- `MCPORACLE_ORACLE_PASSWORD`
- `MCPORACLE_ORACLE_DSN`

## Запуск сервера

После установки:

```powershell
mcporacle
```

Альтернатива:

```powershell
python -m mcporacle.server
```

Сервер стартует как локальный MCP server поверх `stdio`, что подходит для интеграции с Roo Code.

## Настройка Roo Code в VSCode

Roo Code поддерживает два уровня конфигурации MCP servers:

- глобальный файл `mcp_settings.json`
- проектный файл `.roo/mcp.json`

Для этого проекта удобнее использовать проектную конфигурацию `.roo/mcp.json`, чтобы настройки были привязаны к конкретному репозиторию.

В интерфейсе Roo Code:

- откройте панель Roo Code в VSCode
- откройте раздел MCP
- нажмите `Edit Project MCP`
- вставьте конфигурацию ниже

### Рекомендуемый вариант: credentials в `.env`

Если в корне проекта уже лежит `.env`, сервер сам его прочитает. В этом случае в конфиге Roo Code достаточно указать команду запуска и `cwd`.

```json
{
  "mcpServers": {
    "mcporacle": {
      "command": "C:\\path\\to\\mcporacle\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcporacle.server"],
      "cwd": "C:\\path\\to\\mcporacle",
      "disabled": false
    }
  }
}
```

Что нужно заменить:

- `C:\\path\\to\\mcporacle` на абсолютный путь к репозиторию
- `C:\\path\\to\\mcporacle\\.venv\\Scripts\\python.exe` на абсолютный путь к Python внутри виртуального окружения проекта

### Альтернатива: credentials прямо в конфиге Roo Code

Если не хотите использовать `.env`, можно передать переменные окружения прямо в настройке MCP server:

```json
{
  "mcpServers": {
    "mcporacle": {
      "command": "C:\\path\\to\\mcporacle\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcporacle.server"],
      "cwd": "C:\\path\\to\\mcporacle",
      "env": {
        "MCPORACLE_ORACLE_USER": "system",
        "MCPORACLE_ORACLE_PASSWORD": "oracle",
        "MCPORACLE_ORACLE_DSN": "localhost:1521/FREEPDB1",
        "MCPORACLE_LOG_LEVEL": "INFO"
      },
      "disabled": false
    }
  }
}
```

### Что важно для запуска

- `cwd` должен указывать на корень репозитория, иначе сервер не найдет локальный `.env`
- путь к `python.exe` лучше указывать абсолютный, чтобы Roo Code не зависел от активированного терминала
- после сохранения `.roo/mcp.json` сервер появится в списке MCP servers в Roo Code
- если сервер был уже запущен с другой конфигурацией, перезапустите его из панели MCP

### Быстрая проверка

После подключения MCP server в Roo Code должен появиться tool `get_table_info`. Дальше можно дать Roo, например, такой запрос:

```text
Используй tool get_table_info для схемы HR и таблицы EMPLOYEES
```

## Tool `get_table_info`

### Вход

```json
{
  "schema_name": "HR",
  "table_name": "EMPLOYEES"
}
```

### Выход

```json
{
  "ok": true,
  "table": {
    "owner": "HR",
    "table_name": "EMPLOYEES",
    "comment": "Employee master data",
    "columns": [
      {
        "name": "EMPLOYEE_ID",
        "data_type": "NUMBER",
        "nullable": false,
        "data_length": 22,
        "data_precision": 10,
        "data_scale": 0,
        "column_id": 1,
        "comment": "Primary key"
      }
    ]
  }
}
```

### Как реализован запрос

Tool вызывает анонимный PL/SQL-блок, который:

- открывает один REF CURSOR для информации о таблице
- открывает второй REF CURSOR для списка колонок
- читает данные из DBA views через bind-параметры

Это позволяет сохранить функциональность строго ограниченной и не принимать SQL от клиента.

## Требования к Oracle

Пользователь Oracle должен иметь возможность читать:

- `DBA_TABLES`
- `DBA_TAB_COMMENTS`
- `DBA_TAB_COLUMNS`
- `DBA_COL_COMMENTS`

Если доступов нет, tool вернет ошибку уровня приложения.

## Тесты

После установки зависимостей:

```powershell
python -m unittest discover -s tests -v
```

## Что пока не входит в MVP

- дополнительные tools кроме `get_table_info`
- пул соединений
- кеширование метаданных
- fallback на `ALL_*`/`USER_*` views
- интеграционные тесты с живой Oracle DB

## Допущения

- Для первого MVP выбран самый простой и безопасный интерфейс: только один tool и только metadata lookup.
- Если у пользователя нет прав на `DBA_*` views, сервер сейчас возвращает понятную ошибку, а не пытается автоматически переключаться на другие словари.
