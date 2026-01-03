@echo off
REM ==============================================================================
REM Script d'evaluation RAGAS pour le chatbot RAG Crypto (Windows)
REM ==============================================================================
REM
REM Usage:
REM   run_evaluation.bat          # Evaluation rapide (5 samples)
REM   run_evaluation.bat full     # Evaluation complete RAGAS
REM   run_evaluation.bat stats    # Statistiques du dataset
REM   run_evaluation.bat query "Quel est le sentiment de Bitcoin?"
REM
REM ==============================================================================

setlocal enabledelayedexpansion

echo =============================================
echo        RAGAS Evaluation - Crypto RAG
echo =============================================

REM Repertoire du script
set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%..

REM Aller dans le repertoire backend
cd /d "%BACKEND_DIR%"

REM Verifier Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERREUR] Python non trouve!
    exit /b 1
)

REM Determiner le mode
set MODE=%1
if "%MODE%"=="" set MODE=quick

if "%MODE%"=="quick" (
    echo.
    echo [Mode: Evaluation rapide - 5 samples]
    echo.
    python scripts/evaluate_rag.py --quick
    goto :done
)

if "%MODE%"=="full" (
    echo.
    echo [Mode: Evaluation complete RAGAS]
    echo.
    python scripts/evaluate_rag.py --full --samples 20
    goto :done
)

if "%MODE%"=="simple" (
    echo.
    echo [Mode: Evaluation simple - heuristiques]
    echo.
    python scripts/evaluate_rag.py --simple --samples 10
    goto :done
)

if "%MODE%"=="stats" (
    echo.
    echo [Mode: Statistiques du dataset]
    echo.
    python scripts/evaluate_rag.py --stats
    goto :done
)

if "%MODE%"=="query" (
    if "%~2"=="" (
        echo [ERREUR] Specifiez une question
        echo Usage: %0 query "Votre question"
        exit /b 1
    )
    echo.
    echo [Mode: Test question unique]
    echo.
    python scripts/evaluate_rag.py --query "%~2"
    goto :done
)

if "%MODE%"=="category" (
    if "%~2"=="" (
        echo [ERREUR] Specifiez une categorie
        echo Categories: sentiment_general, comparison, correlation, temporal, detailed, vague, faq
        exit /b 1
    )
    echo.
    echo [Mode: Evaluation categorie '%2']
    echo.
    python scripts/evaluate_rag.py --category %2 --samples 5
    goto :done
)

if "%MODE%"=="help" (
    echo.
    echo Usage: %0 [MODE] [OPTIONS]
    echo.
    echo Modes disponibles:
    echo   quick      Evaluation rapide ^(5 samples, heuristiques^) [defaut]
    echo   full       Evaluation complete avec RAGAS ^(20 samples^)
    echo   simple     Evaluation heuristiques ^(10 samples^)
    echo   stats      Afficher les statistiques du dataset
    echo   query      Tester une question: %0 query "Question?"
    echo   category   Evaluer une categorie: %0 category comparison
    echo   help       Afficher cette aide
    echo.
    echo Categories:
    echo   sentiment_general, comparison, correlation
    echo   temporal, detailed, vague, faq
    echo.
    goto :done
)

echo [ERREUR] Mode inconnu: %MODE%
echo Utilisez '%0 help' pour voir les options
exit /b 1

:done
echo.
echo [Done!]
endlocal
