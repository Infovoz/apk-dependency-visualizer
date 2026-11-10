@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PY_BIN=.venv\Scripts\python.exe"
) else (
    set "PY_BIN=python"
)

if "%~1"=="" (
    echo [Запуск без аргументов]
    set /p PKG="Введите имя пакета (например, curl): "
    set /p REPO="Введите URL репозитория или путь к файлу: "
    set /p DEPTH="Введите макс. глубину (Enter для пропуска): "

    if "!DEPTH!"=="" (
        "%PY_BIN%" -m src.main --package "!PKG!" --repo "!REPO!" --ascii-tree
    ) else (
        "%PY_BIN%" -m src.main --package "!PKG!" --repo "!REPO!" --max-depth !DEPTH! --ascii-tree
    )
) else (
    "%PY_BIN%" -m src.main %*
)

if errorlevel 1 (
    echo.
    echo [ERROR] Скрипт завершился с ошибкой.
    pause
) else (
    echo.
    echo [УСПЕШНО] Выполнение завершено.
    pause
)