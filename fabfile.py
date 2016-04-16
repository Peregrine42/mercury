from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import upload_template
import re
import sys
import os

env.roledefs["rpis"] = ["192.168.33.15", "192.168.33.16"];
rpi_passwords = map(
    lambda i: os.environ.get(
        'MERCURY_RPI' + str(i) + "_PASSWORD", 
        "password"
    ),
    range(0, len(env.roledefs["rpis"]))
)
if rpi_passwords.index("password") > -1:
    print "WARNING: deploying default",\
          "password to at least one rpi!";

env.roledefs["loggers"] = ["192.168.33.10"]
env.parallel = True

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
            "id": "rpi" + str(
                env.roledefs["rpis"].index(env.host)
            ),
            "home": "https://" + env.roledefs["loggers"][0],
            "password": 
                rpi_passwords[
                    env.roledefs["rpis"].index(env.host)
                ]
        }
    )
    sudo("chmod +x /home/mercury/sync.sh")

    upload_template_as_user(
        "mercury",
        "templates/rpi/cacert.pem",
        "/home/mercury/cacert.pem",
        context = {}
    )

    upload_template_as_user(
        "root",
        "templates/rpi/phone_home.service",
        "/etc/systemd/system/phone_home.service",
        context = {}
    )

    upload_template_as_user(
        "root",
        "templates/rpi/phone_home_startup.service",
        "/etc/systemd/system/phone_home_startup.service",
        context = {}
    )
    sudo("systemctl daemon-reload")

    sudo("systemctl restart phone_home_startup")
    sudo("systemctl enable phone_home_startup")

    sudo("systemctl restart phone_home")
    sudo("systemctl enable phone_home")

@roles("loggers")
def logger():
    sudo("yum install -y epel-release")
    sudo("yum install -y nginx httpd-tools")

    sudo("touch /etc/nginx/.htpasswd")

    for i, password in enumerate(rpi_passwords):
        sudo("htpasswd -b /etc/nginx/.htpasswd " 
            + "rpi" + str(i) + " " + password)

        sudo("mkdir -p /usr/share/nginx/html/rpi/rpi" + str(i))
        upload_template_as_user(
            "root",
            "templates/logger/basic_crontab",
            "/usr/share/nginx/html/rpi/rpi"
            + str(i) + "/crontab",
            context = {}
        )
        put(
            "logger/payload.tar.gz",
            "/usr/share/nginx/html/rpi/rpi"
            + str(i) + "/payload.tar.gz",
            use_sudo=True
        )

    sudo("mkdir -p /etc/nginx/ssl")
    upload_template_as_user(
        "root",
        "templates/logger/nginx.crt",
        "/etc/nginx/ssl/nginx.crt"
    )
    upload_template_as_user(
        "root",
        "templates/logger/nginx.key",
        "/etc/nginx/ssl/nginx.key"
    )

    upload_template_as_user(
        "root",
        "templates/logger/nginx.conf",
        "/etc/nginx/nginx.conf",
        context = { "ip": env.roledefs["loggers"][0] }
    )

    sudo("systemctl enable nginx")
    sudo("systemctl restart nginx")
