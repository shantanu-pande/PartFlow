FROM python

# Set the working directory
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . ./ 

EXPOSE 5000

CMD [ "streamlit", "run", "main.py"]
