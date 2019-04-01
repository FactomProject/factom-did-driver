FROM alpine:3.4
MAINTAINER Sam Barnes <sam.barnes@factom.com>

RUN apk add --update \
python3 \
python3-dev \
py-pip \
build-base \
git \
&& rm -rf /var/cache/apk/*

RUN pip3 install --upgrade pip
RUN pip3 install gunicorn

RUN addgroup -S apprunner
RUN adduser -G apprunner -S apprunner

COPY . .

RUN pip3 install -r requirements.txt
RUN pip3 install git+https://github.com/sambarnes/factom-api.git

ENV uniresolver_driver_did_factom_factomConnection=harmony_connect
ENV uniresolver_driver_did_factom_rpcUrlMainnet=https://api.factomd.net
ENV uniresolver_driver_did_factom_rpcUrlTestnet=https://localhost:8088
ENV uniresolver_driver_did_factom_harmonyConnectApi=https://api.factom.com/v1

EXPOSE 8080

CMD cd src && gunicorn -b :8080 did_factom_driver:app