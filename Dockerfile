FROM debian:bookworm
LABEL org.opencontainers.image.source=https://github.com/makerspacelt/slack-ical-upcoming-events
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -y && \
    apt-get install -y python3-pip tzdata git
# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt
COPY . /app
ENTRYPOINT ["python3"]
CMD ["main.py"]
