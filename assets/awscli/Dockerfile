FROM registry.access.redhat.com/ubi8/ubi:latest
LABEL maintainer="Stephen Cuppett <scuppett@redhat.com>"

RUN dnf -y update; dnf -y install procps python3 python3-pip; dnf -y clean all
RUN pip3 install awscli --upgrade

CMD ["aws", "--version"]

