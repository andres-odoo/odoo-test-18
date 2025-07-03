ARG IMAGE_TAG=e18.0
FROM gitlab.syscoon.com:5050/internal/odoo-ci/odoo:$IMAGE_TAG

USER root

COPY ./internal_addons /mnt/odoo/internal_addons
COPY ./external_addons /mnt/odoo/external_addons
COPY ./config /mnt/config

# Install Dependancies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev
RUN apt-get install --reinstall python3-pip

# Only to install current project requirements
COPY ./requirements.txt /mnt/odoo/
RUN pip3 install -r /mnt/odoo/requirements.txt --break-system-packages

USER odoo
