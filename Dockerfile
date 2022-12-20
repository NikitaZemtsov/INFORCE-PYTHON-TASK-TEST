FROM python:3.10
COPY . /app
EXPOSE 5005
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:5005", "manage:app"]