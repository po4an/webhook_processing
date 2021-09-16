#!/bin/bash
docker run --network=webhook_processing_default --rm -v C://Users//grish//PycharmProjects//testtest//webhook_processing//liquibase//:/liquibase/changelog liquibase/liquibase --driver=org.postgresql.Driver --url="jdbc:postgresql://postgres:5432/test" --username=test --password=test --changelogFile=root.changelog.xml update
