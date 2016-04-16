export MERCURY_LOGGER_HOME="%(home)s"
export MERCURY_ID="%(id)s"
export MERCURY_PASSWORD="%(password)s"

MESSAGE=`curl -L -u $ID:$MERCURY_PASSWORD --cacert /home/mercury/cacert.pem $MERCURY_LOGGER_HOME/rpi/$MERCURY_ID/crontab`
echo "$MESSAGE" | /bin/crontab

curl -L --cacert /home/mercury/cacert.pem $MERCURY_LOGGER_HOME/rpi/$MERCURY_ID/payload.tar.gz | tar zxf - -C /dev/shm/
