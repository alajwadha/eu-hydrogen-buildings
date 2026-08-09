@echo off
title EU Hydrogen Buildings — Run Pipeline
cd /d "%~dp0"

echo.
echo ============================================================
echo  EU Hydrogen Buildings Model
echo ============================================================
echo.

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Add MiKTeX to PATH
set PATH=%PATH%;%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64

echo What do you want to do?
echo.
echo   1. Run STATED_POLICIES scenario
echo   2. Run NET_ZERO scenario
echo   3. Run H2_PUSH scenario
echo   4. Regenerate figures only
echo   5. Build PDF only
echo   6. Update literature
echo   7. Push to GitHub
echo   8. Run everything (STATED_POLICIES + figures + PDF + push)
echo.
set /p choice="Enter number (1-8): "

if "%choice%"=="1" goto run_ref
if "%choice%"=="2" goto run_high_hp
if "%choice%"=="3" goto run_h2
if "%choice%"=="4" goto figures
if "%choice%"=="5" goto pdf
if "%choice%"=="6" goto literature
if "%choice%"=="7" goto push
if "%choice%"=="8" goto run_all
goto end

:run_ref
echo.
echo Running STATED_POLICIES scenario...
python run.py --scenario STATED_POLICIES --skip-download
goto end

:run_high_hp
echo.
echo Running NET_ZERO scenario...
python run.py --scenario NET_ZERO --skip-download
goto end

:run_h2
echo.
echo Running H2_PUSH scenario...
python run.py --scenario H2_PUSH --skip-download
goto end

:figures
echo.
echo Regenerating figures...
python code\scripts\make_figures.py --all
goto end

:pdf
echo.
echo Building PDF...
cd paper
pdflatex -interaction=nonstopmode Paper_v1.tex
bibtex Paper_v1
pdflatex -interaction=nonstopmode Paper_v1.tex
pdflatex -interaction=nonstopmode Paper_v1.tex
cd ..
echo.
echo PDF built: paper\Paper_v1.pdf
start paper\Paper_v1.pdf
goto end

:literature
echo.
echo Searching for new papers...
python code\scripts\update_literature.py
echo.
echo Done. Check literature\new_papers.md for results.
start literature\new_papers.md
goto end

:push
echo.
set /p msg="Commit message: "
git add .
git commit -m "%msg%"
git push
echo.
echo Pushed to GitHub.
goto end

:run_all
echo.
echo Running full pipeline...
echo.
echo [1/4] Running STATED_POLICIES scenario...
python run.py --scenario STATED_POLICIES --skip-download
echo.
echo [2/4] Regenerating all figures...
python code\scripts\make_figures.py --all
echo.
echo [3/4] Building PDF...
cd paper
pdflatex -interaction=nonstopmode Paper_v1.tex
bibtex Paper_v1
pdflatex -interaction=nonstopmode Paper_v1.tex
pdflatex -interaction=nonstopmode Paper_v1.tex
cd ..
echo.
echo [4/4] Pushing to GitHub...
git add .
git commit -m "Auto: STATED_POLICIES results, figures, and PDF updated"
git push
echo.
echo All done! Opening PDF...
start paper\Paper_v1.pdf
goto end

:end
echo.
pause
