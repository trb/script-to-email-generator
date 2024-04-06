FROM python

COPY script-to-email/lib/ /app/lib/
COPY script-to-email/__init__.py script-to-email/script-to-email.py script-to-email/requirements.txt /app/

WORKDIR /app

VOLUME ["/app"]
VOLUME ["/scripts"]
VOLUME ["/output"]

RUN apt-get update && apt-get full-upgrade -y \
 && pip3 install -r /app/requirements.txt

ENTRYPOINT ["python3", "script-to-email.py", "/scripts"]
