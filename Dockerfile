FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    apt-get clean

COPY . .

RUN pip install --no-cache-dir -r requirements.txt && chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]