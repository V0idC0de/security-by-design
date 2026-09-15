FROM python:3.14.7-alpine3.24@sha256:05b2b8b732ecd268fee8727a369f936f022d1321b59befd13c30ede22769dcdc

RUN adduser -H -D -s /bin/sh appuser
RUN mkdir /app
COPY app.py /app/app.py
RUN chown -R appuser:appuser /app

USER appuser
WORKDIR /app

ENV GREETED=Students
ENV PORT=8000

CMD ["python", "app.py"]