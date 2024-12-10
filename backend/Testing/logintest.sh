#!/bin/bash

sendlogin() {
	printf "$(curl -siX POST http://localhost:5000/login \
		-H "Content-Type: application/json" \
		-d "{\"username\": \"$1\", \"password\": \"$2\"}")"
}


test_success_rate=0

clear
echo "Testing the login functionality"


printf "\nTest 1: existing username with correct password\n"

login=$(printf "$(sendlogin "test_user" "test")" | \
	grep -e "Set-Cookie: session=.*-*.*.*-*"  -e "\"success\": true," | \
	wc -l)
if [ $login -eq 2 ]; then
	echo "Test was sucessful"
	((test_success_rate++))
else
	echo "Test failed"
fi


printf "\nTest 2: existing username with incorrect password\n"

login=$(printf "$(sendlogin "test_user" "passwd")" |  \
	grep -e "Set-Cookie: session=.*-*.*.*-*" -e "\"success\": false" | \
	wc -l)
if [ $login -eq 1 ]; then
	echo "Test was sucessful"
	((test_success_rate++))
else
	echo "Test failed"
fi


printf "\nTest 3: nonexisting username with incorrect password\n"

login=$(printf "$(sendlogin "test_user" "passwd")" |  \
	grep -e "Set-Cookie: session=.*-*.*.*-*" -e "\"success\": false" | \
	wc -l)
if [ $login -eq 1 ]; then
	echo "Test was sucessful"
	((test_success_rate++))
else
	echo "Test failed"
fi


printf "\nTest 4: existing username, password empty\n"

login=$(printf "$(sendlogin "test_user" "")" |  \
	grep -e "Set-Cookie: session=.*-*.*.*-*" -e "\"success\": false" | \
	wc -l)
if [ $login -eq 1 ]; then
	echo "Test was sucessful"
	((test_success_rate++))
else
	echo "Test failed"
fi


printf "\nTest 5: empty username, existing password\n"

login=$(printf "$(sendlogin "" "test")" |  \
	grep -e "Set-Cookie: session=.*-*.*.*-*" -e "\"success\": false" | \
	wc -l)
if [ $login -eq 1 ]; then
	echo "Test was sucessful"
	((test_success_rate++))
else
	echo "Test failed"
fi


printf "\nTest 6: both username and password are empty\n"

login=$(printf "$(sendlogin "" "")" |  \
	grep -e "Set-Cookie: session=.*-*.*.*-*" -e "\"success\": false" | \
	wc -l)
if [ $login -eq 1 ]; then
	echo "Test was sucessful"
	((test_success_rate++))
else
	echo "Test failed"
fi


printf "\nTesting completed\n$test_success_rate/6 tests were sucessful!\n"
