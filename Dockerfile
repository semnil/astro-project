FROM quay.io/astronomer/ap-airflow:1.10.7-alpine3.10-onbuild

RUN apk add --no-cache postgresql

RUN apk add --no-cache zip

RUN apk add --no-cache \
        python3 \
        py3-pip \
    && pip3 install --upgrade pip \
    && pip3 install \
        awscli
