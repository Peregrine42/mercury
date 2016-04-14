from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import upload_template
import re
import sys

env.parallel = True

env.roledefs["rpis"] = ["192.168.33.15"]
env.roledefs["loggers"] = ["192.168.33.10"]

rpi_ids = ["rpi5"]

def vagrant():
    result = local('vagrant ssh-config', capture=True)
    env.user = re.findall(r'User\s+([^\n]+)', result)[0]
    env.key_filename = \
	re.findall(r'IdentityFile\s+"([^"]+)', result)[0]

def upload_template_as_user(user, source, target, **kwargs):
    kwargs["use_sudo"] = True
    upload_template(
        source,
        target,
        **kwargs
    )
    sudo(("chown -R %s:%s " % (user, user)) + target)
    sudo("chmod -R +r " + target)
    sudo("chmod -R +w " + target)

@roles("rpis")
def rpis():
    # set up mercury
    sudo("id -u mercury || adduser mercury")

    # set up phone_home.sh
    sudo("mkdir -p /home/mercury/payload")
    sudo("chown -R mercury:mercury /home/mercury/payload")
    upload_template_as_user(
        "mercury",
        "templates/rpi/phone_home.sh",
        "/home/mercury/phone_home.sh",
        context = { 
            "interval": 5,
            "timeout": 4
        }
    )
    sudo("chmod +x /home/mercury/phone_home.sh")

    upload_template_as_user(
        "mercury",
        "templates/rpi/sync.sh",
        "/home/mercury/sync.sh",
        context = { 
            "id": rpi_ids[0], 
            "home": env.roledefs["loggers"][0],
        }
    )
    sudo("chmod +x /home/mercury/sync.sh")

    upload_template_as_user(
        "mercury",
        "templates/rpi/cacert.pem",
        "/home/mercury/cacert.pem",
        context = { }
    )

    upload_template_as_user(
        "root",
        "templates/rpi/phone_home.service",
        "/etc/systemd/system/phone_home.service",
        context = {}
    )
    sudo("systemctl daemon-reload")
    sudo("systemctl restart phone_home")
    sudo("systemctl enable phone_home")

@roles("loggers")
def logger():
    sudo("yum install -y epel-release")
    sudo("yum install -y nginx httpd-tools")
    sudo("systemctl enable nginx")
    sudo("systemctl restart nginx")

    sudo("mkdir -p /usr/share/nginx/html/rpi/rpi5")
    upload_template_as_user(
        "root",
        "templates/logger/basic_crontab",
        "/usr/share/nginx/html/rpi/rpi5/crontab",
        context = {}
    )
    put("logger/payload.tar.gz", "/usr/share/nginx/html/rpi/rpi5/payload.tar.gz", use_sudo=True)

    sudo("mkdir /etc/nginx/ssl")
    upload_template_as_user(
        "root",
        "templates/logger/nginx.conf",
        "/etc/nginx/nginx.conf",
        context = { "ip": env.roledefs["loggers"][0] }
    )

