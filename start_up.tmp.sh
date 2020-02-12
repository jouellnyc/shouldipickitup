/usr/local/bin/gunicorn -w 4 --bind=0.0.0.0:8000 --log-level=debug app:app --access-logfile access.log &

# service docker start
# service nginx start

#systemctl status nginx | grep -i enab
#   Loaded: loaded (/usr/lib/systemd/system/nginx.service; enabled; vendor preset: disabled)

#systemctl status docker  | grep -i enab
#   Loaded: loaded (/usr/lib/systemd/system/docker.service; enabled; vendor preset: disabled)

