# MVP-Paytool-Bot

### формат .env
```bash
BOT_TOKEN=
ADMINS=123456789,987654321    # все ID админов через запятую
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```
# как запустить?

### тыкаешь консольку создаешь окружение 

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### поднимаешь Redis для проекта

```bash
docker compose up -d
```

на всякий чекни что все воркает

``` bash
docker ps   #должен быть контейнер с именем MVP-Paytool-Bot_redis
docker exec -it MVP-Paytool-Bot_redis redis-cli   #так перейдешь в контейнер
PING   # получаешь ответ PONG значит все работатет 
```
