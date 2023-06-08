FROM hashicorp/terraform

ADD environments .
ADD modules .
ADD deploy.sh

ENV environment=dev

RUN deploy.sh $environment