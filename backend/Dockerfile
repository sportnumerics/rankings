FROM python:3.8
WORKDIR /app
RUN pip install pipenv
ADD Pipfile.lock .
RUN pipenv install --ignore-pipfile
ADD Pipfile .
ADD lib lib
ADD main.py .
CMD ["pipenv", "run", "main"]