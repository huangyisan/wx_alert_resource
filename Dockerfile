FROM alpine
MAINTAINER anonymousyisan@gmail.com

RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python


