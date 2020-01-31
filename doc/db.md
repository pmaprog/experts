# EventsProj Database

## Почему PostgreSQL
* Хорошая докумантция и большое сообщество.
* Поддержка множества дополнительных типов, например UUID, JSONB и другие.
* Следует ACID (в отличии от MySQL/InnoDB).
* Шардирование из коробки.

Но в то же время проигрывает MySQL по скорости работы.

## Как поставить PostgreSQL 
1) Ставим пакет:
	
	Ubuntu:

		sudo apt install -y postgresql
	
	CentOS 7:

		sudo yum install postgresql-server postgresql-contrib
		sudo postgresql-setup initdb
		sudo systemctl start postgresql

2) Переходим в суперюзера бд:

		sudo su - postgres

3) Создаём новую роль:

		createuser %usename% --pwprompt

4) Создаём саму БД:

		createdb -O %username% %dbname%

5) Подключаемся к новой БД и даем доступы:

		psql %dbname% 
		GRANT ALL ON DATABASE %dbname% to %username%;

6) CENTOS ONLY! Отредактировать конфиг-файл:

		cd /var/lib/pgsql/data/
		sudo nano/vim ph_hba.conf
		заменить METHOD на md5 у local, ipv4, ipv6 connections (3 записи).
