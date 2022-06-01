FROM python:3.8-slim

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
WORKDIR /usr/local/Scraping_MLcars
EXPOSE 8000

COPY . ./

# This command will make the container to continue running
CMD ["tail", "-f", "/dev/null"]
