FROM python:3-alpine
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . /app
CMD [ "python", "main.py", "daemon" ]