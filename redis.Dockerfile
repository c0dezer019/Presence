FROM redis

RUN mkdir -p /var/lib/redis \
    && chown redis:redis /var/lib/redis

COPY redis.conf /usr/local/etc/redis/redis.conf

CMD [ "redis-server", "/usr/local/etc/redis/redis.conf"]
