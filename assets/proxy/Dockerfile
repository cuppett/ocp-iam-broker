FROM registry.access.redhat.com/ubi8/ubi:latest
LABEL maintainer="Stephen Cuppett <scuppett@redhat.com>"

EXPOSE 53080

RUN dnf -y install nginx

COPY nginx.conf.TEMPLATE /etc/nginx/nginx.conf.TEMPLATE
COPY docker-entrypoint.sh ./docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
