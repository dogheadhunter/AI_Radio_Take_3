FROM python:3.10-slim
WORKDIR /app
COPY app.py /app/app.py
RUN pip install flask
EXPOSE 3000
CMD ["python", "app.py"]
