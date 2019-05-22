#!/bin/sh

aws s3 cp s3://openprecincts-internal/backups/openprecincts_testdb.pgdump .
pg_restore --no-owner -U openprecincts -d openprecincts -h localhost -p 5432 openprecincts_testdb.pgdump
