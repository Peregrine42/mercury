LOGGER_HOME="%(home)s"
ID="%(id)s"

curl $LOGGER_HOME/rpi/$ID/crontab | /bin/crontab
curl $LOGGER_HOME/rpi/$ID/payload.tar.gz | tar zxf - -C /home/mercury/
