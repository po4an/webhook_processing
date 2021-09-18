#!/bin/bash
docker run --network=airflow_default --rm -v C://Users//grish//PycharmProjects//testtest//webhook_processing//airflow//liquibase//:/liquibase/changelog liquibase/liquibase --driver=org.postgresql.Driver --url="jdbc:postgresql://main_db:5432/hqddb" --username=hqduser --password=hqdpassword --changelogFile=root.changelog.xml update
