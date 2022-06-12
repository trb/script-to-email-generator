FROM python

COPY script-to-email/* /app/

WORKDIR /app

VOLUME ["/app"]
VOLUME ["/scripts"]
VOLUME ["/output"]

RUN apt-get update && apt-get full-upgrade -y
RUN pip install -r /app/requirements.txt

ENTRYPOINT ["python", "script-to-email.py", "/scripts"]
