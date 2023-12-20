FROM python:3.11.5

WORKDIR /ImageToExcelConverter

COPY . /ImageToExcelConverter

RUN pip install -r requirements.txt

CMD ["python", "app/main.py"]
