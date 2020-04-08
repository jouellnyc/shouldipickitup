workers = 4
bind = "0.0.0.0:8000"
accesslog = 'access.log'
access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s'
