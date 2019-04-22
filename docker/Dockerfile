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

# possible environment variables
#ENV uniresolver_driver_did_factom_factomConnection=factomd
#ENV uniresolver_driver_did_factom_rpcUrlMainnet=https://api.factomd.net
#ENV uniresolver_driver_did_factom_rpcUrlTestnet=https://dev.factomd.net
#ENV uniresolver_driver_did_factom_tfaExplorerApiUrlMainnet=https://explorer.factoid.org/api/v1
#ENV uniresolver_driver_did_factom_tfaExplorerApiUrlTestnet=https://testnet.factoid.org/api/v1
#ENV uniresolver_driver_did_factom_harmonyApiUrl=https://api.factom.com/v1
#ENV uniresolver_driver_did_factom_harmonyApiAppId=APP_ID
#ENV uniresolver_driver_did_factom_harmonyApiAppKey=APP_KEY
#ENV uniresolver_driver_did_factom_harmonyApiCachingEnabled=false

EXPOSE 8080

CMD gunicorn -b :8080 did_factom_driver:app