FROM public.ecr.aws/lambda/python:3.9 as stage

# Hack to install chromium dependencies
RUN yum install -y -q sudo unzip

# Current stable version of Chromium
ENV CHROMIUM_VERSION=1002910 

# Install Chromium
COPY install-browser.sh /tmp/
RUN /usr/bin/bash /tmp/install-browser.sh

FROM public.ecr.aws/lambda/python:3.9 as base

COPY chrome-deps.txt /tmp/
RUN yum install -y $(cat /tmp/chrome-deps.txt)

COPY --from=stage /opt/chrome /opt/chrome
COPY --from=stage /opt/chromedriver /opt/chromedriver

COPY create.py ${LAMBDA_TASK_ROOT}
COPY process.py ${LAMBDA_TASK_ROOT}
COPY get_status.py ${LAMBDA_TASK_ROOT}
COPY web_driver_wrapper.py ${LAMBDA_TASK_ROOT}


COPY requirements.txt ${LAMBDA_TASK_ROOT}
COPY db/ ${LAMBDA_TASK_ROOT}/db/   

RUN python3.9 -m pip install -r requirements.txt -t .

