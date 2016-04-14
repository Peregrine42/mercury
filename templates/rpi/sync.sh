LOGGER_HOME="%(home)s"
ID="%(id)s"

MESSAGE=`curl $LOGGER_HOME/rpi/$ID/crontab`
echo "$MESSAGE" | tail -n +2 | /bin/crontab

curl $LOGGER_HOME/rpi/$ID/payload.tar.gz | tar zxf - -C /home/mercury/
