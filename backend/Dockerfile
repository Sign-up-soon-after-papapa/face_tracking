FROM python:3.8-alpine

LABEL description="Hackathon 2020 database API" \
      version="V1" \
      author="MiaoTony"

WORKDIR /usr/src/hackathon

USER root

ENV TZ=Asia/Shanghai

RUN	sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
	&& apk update && apk add --no-cache bash gcc vim curl wget g++ make linux-headers libffi-dev openssl-dev libxml2 libxml2-dev libxslt libxslt-dev tzdata  \
	&& addgroup -S hackathon && adduser -S -G hackathon hackathon

COPY requirements.txt ./
RUN	ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime  \
        && echo "Asia/Shanghai" > /etc/timezone  \
	&& pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U  \
	&& pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple  \
	&& pip3 install --no-cache-dir --upgrade setuptools wheel \
	&& pip3 install --no-cache-dir -r requirements.txt  \
	&& rm -rf /tmp/* /usr/local/lib/php/doc/* /var/cache/apk/*

COPY . .

EXPOSE 9800

USER hackathon

CMD ["backend:app", "-c", "./gunicorn.conf.py", "--log-level=debug" ]

ENTRYPOINT [ "gunicorn" ]
