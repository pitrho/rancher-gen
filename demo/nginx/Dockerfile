FROM phusion/baseimage:0.9.17
MAINTAINER pitrho

# Step 1 - Install nginx and python
ENV DEBIAN_FRONTEND noninteractive
RUN \
  apt-add-repository -y ppa:nginx/stable && \
  apt-get update && \
  apt-get install -y python-software-properties \
    wget \
    nginx \
    python-dev \
    python-pip \
    libev4 \
    libev-dev \
    expect-dev && \
  rm -rf /var/lib/apt/lists/* && \
  chown -R www-data:www-data /var/lib/nginx && \
apt-get clean

# Step 2 - Install rancher-gen
ENV RANCHER_GEN_VERSION 0.1.2
RUN pip install rancher-gen==$RANCHER_GEN_VERSION

# Step 3 - Define services
RUN mkdir /etc/service/nginx /etc/service/rancher_gen /nginxconf
COPY nginx_run /etc/service/nginx/run
COPY rancher-gen_run /etc/service/rancher_gen/run
COPY default.j2 /nginxconf

# Step 4 - Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

# Step 5 - Expose ports.
EXPOSE 80
EXPOSE 443
