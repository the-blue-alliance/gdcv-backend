FROM gcr.io/tbatv-prod-hrd/gdcv-base:latest
MAINTAINER The Blue Alliance

COPY start-prod-gdcv.sh /start.sh
CMD ["/start.sh"]
