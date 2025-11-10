# ADR-006: Security заголовки

## Context

Браузеры используют HTTP заголовки для защиты от распространенных атак (XSS, clickjacking, MIME sniffing).

## Decision

Добавить security middleware для установки заголовков:
- `X-Content-Type-Options: nosniff` - защита от MIME sniffing
- `X-Frame-Options: DENY` - защита от clickjacking
- `X-XSS-Protection: 1; mode=block` - базовая XSS защита

## Alternatives

1. **Без заголовков** - уязвимо к browser-based атакам
2. **nginx/reverse proxy** - требует внешней конфигурации
3. **Расширенные CSP заголовки** - избыточно для API

## Consequences

**Положительные:**
- Защита от clickjacking и MIME sniffing

**Отрицательные:**
- Не защищает полностью от XSS (нужна валидация)

## Security Impact

- Предотвращение встраивания в iframe (clickjacking)
- Блокировка MIME type confusion
- Дополнительная защита от XSS в браузерах
