'''
This code is to test endurance of session against brute force and tampering
This might take a while to run

Function to be tested
def generate_session_id():
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    return session_id

'''

import random
import string

## function to be tested (function used in backend/src/DB.py to generate session id)
def generate_session_id():
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    return session_id

List_to_save_session_ids = []
random_session_id = generate_session_id()

## genrating 10000000 session ids using same function to check if same session id is generated
for i in range(10000000):
    session_id = generate_session_id()
    List_to_save_session_ids.append(session_id)

## checking if all session ids are unique
def test_unique_session_ids():
    return len(set(List_to_save_session_ids)) == len(List_to_save_session_ids)

## check if random_session_id is not in List_to_save_session_ids
def test_random_session_id():
    return random_session_id not in List_to_save_session_ids

## print test results
print("All session ids are unique: ", test_unique_session_ids())
print("Random session id is not in the list: ", test_random_session_id())

