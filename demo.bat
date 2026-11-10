@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PY_BIN=.venv\Scripts\python.exe"
) else (
    set "PY_BIN=python"
)

set "REPO=https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64/APKINDEX.tar.gz"

:menu
cls
echo ==============================================================================
echo         ДЕМОНСТРАЦИОННОЕ МЕНЮ: ПРАКТИЧЕСКАЯ РАБОТА №2 (ВАРИАНТ 18)
echo ==============================================================================
echo  1. Запустить все модульные тесты (13 тестов)
echo  2. Тест: Ромбовидный граф (порядок загрузки D -> B, C -> A)
echo  3. Тест: Циклический граф (отлов цикла C -> A)
echo  4. Alpine: Пакет curl (глубина 2 + ASCII-дерево + PlantUML)
echo  5. Alpine: Пакет python3 (глубина 2 + ASCII-дерево + PlantUML)
echo  6. Alpine: Пакет git (глубина 2 + ASCII-дерево + PlantUML)
echo  7. Полная непрерывная демонстрация (все этапы подряд)
echo  8. Выход
echo ==============================================================================
set /p choice="Выберите пункт (1-8): "

if "%choice%"=="1" goto run_tests
if "%choice%"=="2" goto run_diamond
if "%choice%"=="3" goto run_cycle
if "%choice%"=="4" goto run_curl
if "%choice%"=="5" goto run_python
if "%choice%"=="6" goto run_git
if "%choice%"=="7" goto run_all
if "%choice%"=="8" exit /b

echo Неверный выбор, попробуйте снова.
timeout /t 2 > nul
goto menu

:run_tests
cls
echo [1/1] Запуск тестового набора...
"%PY_BIN%" -m unittest discover tests
echo.
pause
goto menu

:run_diamond
cls
echo [Этап 3-4] Проверка порядка загрузки на тестовом графе diamond_repo.txt...
"%PY_BIN%" -m src.main --test-mode --package A --repo test_data/diamond_repo.txt --ascii-tree
echo.
pause
goto menu

:run_cycle
cls
echo [Этап 3] Проверка обнаружения цикла в cycle_repo.txt...
"%PY_BIN%" -m src.main --test-mode --package A --repo test_data/cycle_repo.txt --ascii-tree
echo.
pause
goto menu

:run_curl
cls
echo [Этап 5] Демонстрация пакета curl...
"%PY_BIN%" -m src.main --package curl --repo "%REPO%" --max-depth 2 --ascii-tree
echo.
pause
goto menu

:run_python
cls
echo [Этап 5] Демонстрация пакета python3...
"%PY_BIN%" -m src.main --package python3 --repo "%REPO%" --max-depth 2 --ascii-tree
echo.
pause
goto menu

:run_git
cls
echo [Этап 5] Демонстрация пакета git...
"%PY_BIN%" -m src.main --package git --repo "%REPO%" --max-depth 2 --ascii-tree
echo.
pause
goto menu

:run_all
cls
echo ==============================================================================
echo 1. ТЕСТЫ ПРОЕКТА
echo ==============================================================================
"%PY_BIN%" -m unittest discover tests
echo.
echo ==============================================================================
echo 2. ТЕСТОВЫЙ РЕПОЗИТОРИЙ: ЦИКЛИЧЕСКАЯ ЗАВИСИМОСТЬ
echo ==============================================================================
"%PY_BIN%" -m src.main --test-mode --package A --repo test_data/cycle_repo.txt --ascii-tree
echo.
echo ==============================================================================
echo 3. РЕАЛЬНЫЙ РЕПОЗИТОРИЙ ALPINE: ПАКЕТ PYTHON3
echo ==============================================================================
"%PY_BIN%" -m src.main --package python3 --repo "%REPO%" --max-depth 2 --ascii-tree
echo.
echo Все ключевые этапы успешно продемонстрированы.
pause
goto menu