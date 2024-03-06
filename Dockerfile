FROM python:3.10.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5001
# CMD to run the application with the command-line arguments
CMD ["python", "keyvaluestore_service.py", "127.0.0.1", "5001", "[['127.0.0.1:5001', '127.0.0.1:5002'],['127.0.0.1:5003', '127.0.0.1:5004']]"]
