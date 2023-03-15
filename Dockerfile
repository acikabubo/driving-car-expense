FROM python:3.9
WORKDIR /project
COPY ./requirements.txt /project/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /project/requirements.txt
COPY . /project
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]