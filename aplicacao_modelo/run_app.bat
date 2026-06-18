@echo off
REM Executa a interface Streamlit do preditor de churn (Vitaliza).
cd /d "%~dp0"

REM Garante dependencias
pip install -r requirements.txt >nul 2>&1

REM Pipeline de treinamento (gera churn_model.joblib + churn_model_full.joblib)
if not exist "churn_model.joblib" (
    echo [1/3] Treinando modelo de churn...
    python train_churn_model.py
)

REM Pipeline de segmentacao (gera segmentation_artifact.joblib)
if not exist "segmentation_artifact.joblib" (
    echo [2/3] Gerando segmentacao/clusters...
    python eda_and_segmentation.py
)

echo [3/3] Iniciando Streamlit em http://localhost:8501
python -m streamlit run app.py
