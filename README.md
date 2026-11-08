# Визуализатор графа зависимостей (Alpine apk)

## 1. Общее описание
Инструмент командной строки для анализа, топологической сортировки и визуализации графа зависимостей пакетов Alpine Linux (apk).

## 2. Описание всех функций и настроек
- `--package`: Имя анализируемого пакета (обязательный).
- `--repo`: URL-адрес официального репозитория (APKINDEX.tar.gz) или путь к тестовому файлу графа.
- `--test-mode`: Режим работы с тестовым репозиторием (флаг).
- `--ascii-tree`: Режим вывода зависимостей в формате ASCII-дерева (флаг).
- `--max-depth`: Максимальная глубина анализа зависимостей (целое число > 0).

## 3. Описание команд для сборки проекта и запуска тестов
- Запуск тестов: `python -m unittest discover tests`
- Запуск через скрипт Windows: `.\run.bat --package curl --repo <URL> --ascii-tree`
- Запуск через bash: `./run.sh --package curl --repo <URL> --ascii-tree`

## 4. Примеры использования
### Пример 1: Анализ пакета curl с глубиной 2
```bash
python -m src.main --package curl --repo [https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64/APKINDEX.tar.gz](https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64/APKINDEX.tar.gz) --max-depth 2 --ascii-tree