FROM nginx:1.16
LABEL maintainer="Stephen Cuppett <scuppett@redhat.com>"

EXPOSE 8080

COPY nginx.conf.TEMPLATE /etc/nginx/nginx.conf.TEMPLATE
COPY docker-entrypoint.sh ./docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
