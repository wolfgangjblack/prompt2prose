#Add official Python Base
FROM python:3.11

#set cwd to /app
WORKDIR /app

#copy the file with requirements
COPY requirements.txt .

#Install package dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

COPY utils/ ./utils

#Run the application
EXPOSE 8000

#set to command to run the uvicorn server
CMD ["python", "main.py"]