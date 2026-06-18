# Deploy containerizado opcional (Render / Railway / Cloud Run) - Aula 07.
# Para Streamlit Community Cloud NAO e necessario: la basta requirements.txt.
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Treina os artefatos no build caso nao tenham sido versionados
RUN python train_churn_model.py && python eda_and_segmentation.py

EXPOSE 8501
# A plataforma injeta a porta em $PORT; localmente cai em 8501.
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]
