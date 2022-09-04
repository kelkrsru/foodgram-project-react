FROM python:3.9-slim
COPY ./ /app
RUN pip install -r /app/requirements.txt --no-cache-dir
WORKDIR /app/
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:5000" ]