python3 manage.py runserver 0.0.0.0:3000 >log.log 2>&1 &

lsof -i :3000
cd Skytronsystem/
python3 manage.py runserver_plus --cert-file cert.pem --key-file key.pem 0.0.0.0:3000 >log.log 2>&1 &
nohup python3 manage.py runserver_plus --cert-file cert.pem --key-file key.pem 0.0.0.0:3000 > log.log 2>&1 &
#python3 manage.py makemigrations
#python3  manage.py migrate
#./run.sh >logError.log &
#https://skytrack.tech:3000/

tmux new -s run_main
tmux new -s run_gps
tmux new -s run_em
tmux new -s run_DL
gunicorn Skytronsystem.wsgi:application



nohup gunicorn --certfile=cert.pem  --keyfile=key.pem -b 0.0.0.0:2000 Skytronsystem.wsgi:application  --static-map /static:/var/www/html/skytron_backend/staticfiles
--static-map /static=/var/www/html/skytron_backend/Skytronsystem/skytron_api/static

nohup  python3 manage.py tcp_server --traceback >logtcp.log 2>&1 &
nohup gunicorn --certfile=cert.pem  --keyfile=key.pem -b 0.0.0.0:2000 Skytronsystem.wsgi:application 

nohup  python3 em_server.py > tcplogem.log 2>&1 &