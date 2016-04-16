export LOGGER_HOME="%(home)s"
export ID="%(id)s"
PASSWORD="%(password)s"

MESSAGE=`curl -L -u $ID:$PASSWORD --cacert /home/mercury/cacert.pem $LOGGER_HOME/rpi/$ID/crontab`
echo "$MESSAGE" | /bin/crontab

curl -L --cacert /home/mercury/cacert.pem $LOGGER_HOME/rpi/$ID/payload.tar.gz | tar zxf - -C /dev/shm/
