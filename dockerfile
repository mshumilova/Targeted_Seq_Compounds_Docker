FROM python 3.11.3

RUN pip install pandas docker

WORKDIR /app

COPY code.py config.py hg37.py hg38.py main.py /app/

CMD ["python3", "main.py"]