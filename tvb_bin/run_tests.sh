#!/bin/bash
# Runs the tests for TVB project.

echo 'Executing clean before tests...'
if [ "$1" ]; then
    # Make sure TVB application is not running....
    python tvb_bin/app.py stop TEST_POSTGRES_PROFILE

	# Run tests using PostgreSQL DB
	python tvb_bin/app.py clean TEST_POSTGRES_PROFILE
	
	echo 'Starting TVB tests on PostgreSQL DB ...'
	mkdir TEST_OUTPUT
	pytest ../framework_tvb/tvb/tests/framework --profile=TEST_POSTGRES_PROFILE --junitxml=TEST_OUTPUT/TEST-RESULTS.xml > TEST_OUTPUT/TEST.out 2>&1
	
else
    # Make sure TVB application is not running....
    python tvb_bin/app.py stop TEST_SQLITE_PROFILE

	# Run tests using SQLite as DB
	python tvb_bin/app.py clean TEST_SQLITE_PROFILE
	
	echo 'Starting TVB tests on SQLite DB ...'
	mkdir TEST_OUTPUT
	pytest --pyargs tvb.tests.framework --junitxml=TEST_OUTPUT/TEST-RESULTS.xml > TEST_OUTPUT/TEST.out 2>&1
fi

echo 'Starting TVB Scientific Library tests'
pytest --pyargs tvb.tests.library --junitxml=TEST_OUTPUT/TEST-LIBRARY-RESULTS.xml > TEST_OUTPUT/TEST-LIBRARY.out 2>&1

echo 'Tests done.'

exit 0

