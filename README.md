# CSV to PostgreSQL Table

This script will take a CSV file and try to guess the correct PostgreSQL table definition which would allow to load this file.

## Sample usage

Given the following file named test_file.csv:

    field1;field2;field3;field4;field5
    1;2012-02-02;1.23;text;1
    2;2012-02-03;2.23;text2;this is actually a string
    2;2012-02-04;3.23;text3;this is actually a string

Running the following command will give you this output:

    ./csv_to_psqltable.py --file=test_file.csv --table=test
    CREATE TABLE test (
    field1 INT, field2 DATE, field3 FLOAT, field4 VARCHAR(5), field5 VARCHAR(25)
    );

You can then create the table and load it with:

\copy test from 'test_file.csv' with delimiter ';' csv header

## Datatypes

The following datatypes are tested:
* float
* integer
* date
* timestamp
* varchar (this is the default if there is no other match)

## Limitations

* Parsing dates is always a bit difficult...
* Delimiters cannot be changed using command line options
* Table / Field names are not escaped properly
* Many types are missing
* ...
