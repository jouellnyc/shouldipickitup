workers = 4
bind = "127.0.0.1:8000"
access-logfile = access.log
access_log_format = %({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"
