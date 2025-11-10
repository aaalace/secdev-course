# ADR-005: Гигиена секретов и конфигурации

## Context

Необходимо исключить попадание секретов в git.

## Decision

Использовать `.env` файлы с библиотекой `python-dotenv`:
- Секреты в `.env` (добавлен в `.gitignore`)
- Шаблон `.env.example` для команды

## Alternatives

1. **Хардкод в коде** - небезопасно, попадает в git
2. **Config файлы (YAML)** - риск коммита секретов
3. **Vault/AWS Secrets Manager** - избыточно

## Consequences

**Положительные:**
- Секреты не в git

**Отрицательные:**
- Нужно вручную создавать `.env`

## Security Impact

- Предотвращение утечки через git
- Изоляция секретов от кода

## Rollout Plan

1. Создать `.env` и `.env.example`
2. Добавить `python-dotenv` в зависимости
3. Использовать `load_dotenv()` в `app/database.py`
4. Настроить `compose.yaml` с переменными окружения
