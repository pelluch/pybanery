import sys
import argparse
import requests
import os
import json
import re
import shutil
from simplecrypt import encrypt, decrypt, DecryptionException

workspace = 'iic215420132'
url = 'https://' + workspace + '.kanbanery.com/api/v1'
headers_get = ''
headers_post = ''
project = '39793'
token = None

# Fix Python 2.x.
try: input = raw_input
except NameError: pass

        
def get_columns():
    r = requests.get(url + '/projects/' + project + '/columns.json', headers=headers_get)
    params = r.json()
    return params

def get_users():
    r = requests.get(url + '/projects/' + project + '/users.json', headers=headers_get)
    params = r.json()
    return params

def search_task(regexp, ignore_cases=True, type=None, estimate_id=None, column=None):
    tasks = get_my_tasks()
    matched = []
    if ignore_cases:
        regexp = regexp.lower()
    for task in tasks:
        title = task['title']
        if ignore_cases:
            title = title.lower()

        match = re.search(regexp, title)
        if match:
            matched.append(task)
            print(str(task['id']) + '\t' + task['title'])



def get_user_info():
    r = requests.get(url + '/user.json', headers=headers_get)
    params = r.json()
    return params['id']

def get_task_types():
    r = requests.get(url + '/projects/' + project + '/task_types.json', headers=headers_get)
    task_types = r.json()
    return task_types

def get_task(task_id):
    r = requests.get(url + '/tasks/' + str(task_id) + '.json', headers=headers_get)
    return r.json()

def get_my_tasks(user_id=None):

    if not user_id:
        user_id = get_user_info()

    user_tasks = []
    tasks = get_all_tasks()
    for task in tasks:
        if task['owner_id'] == user_id:
            user_tasks.append(task)
    return user_tasks

def get_all_tasks():
    r = requests.get(url + '/projects/' + project + '/tasks.json', headers=headers_get)
    params = r.json()
    return params


def set_token(token):
    global headers_get
    global headers_post
    headers_get = {'X-Kanbanery-ApiToken' : token }
    headers_post = dict(headers_get)
    headers_post['Content-Type'] = 'application/json'
    #headers_post['Accept'] = 'application/json'

def validate_token(token):
    set_token(token)
    r = requests.get(url + '/user.json', headers=headers_get)
    if r.status_code == 401:
        print('Invalid user token')
        return False
    else:
        params = r.json()
        print('Welcome, ' + params['name'])
        return True

def create_resource_dict(resources, key='name', make_choice=True, capitalize=False, mult=False):

    params = {}
    for idx, resource in enumerate(resources):
        name = str(resource[key])
        if capitalize:
            name = name.lower().capitalize()
        params[str(idx+1)] = resource
        print(str(idx+1) + '. ' + name)

    str_choice = ''
    if make_choice:     
        if mult:
            valid = False
            while not valid:
                valid = True
                str_choice = input('Enter your choices (1 2 3-5 etc): \n').split(' ')
                chosen = []
                for choice in str_choice:
                    if '-' in choice:
                        nums = choice.split('-')
                        if len(nums) != 2:
                            print('Invalid range: ' + choice)
                            valid = False   
                        try:
                            first = int(nums[0])
                            last = int(nums[1])
                            if first <= last and nums[0] in params and nums[1] in params:
                                for i in range(first, last + 1):
                                    chosen.append(str(i))
                            else:
                                print('Numbers out of range')
                                valid = False
                        except ValueError:
                            print('Range does not include proper numbers')
                            valid = False
                    else:
                        if choice in params:
                            chosen.append(choice)
                        else:
                            print('Selection invalid')
                            valid = False
                chosen = sorted(set(chosen))
                return (chosen, params)

        else:
            while str_choice not in params:
                str_choice = input('Enter your choice: ')
            res_id = params[str_choice]['id']
            return (res_id, params)

    return params

def erase_credentials():
    pybanery_dir = os.path.expanduser("~") + '/.pybanery'
    if os.path.isdir(pybanery_dir):
        shutil.rmtree(pybanery_dir)

def create_task_object(title, column_id, description, estimate_id, owner_id, 
    task_type_id, priority=1):
    task_create = {'task': { 'title' : title, 'task_type_id' : task_type_id, 'column_id' : column_id,
    'description' : description, 'estimate_id' : estimate_id, 'owner_id' : owner_id,
    'priority' : priority}}
    
    r = requests.post(url + '/projects/' + project + '/tasks.json', headers=headers_post, data=json.dumps(task_create))
    if r.status_code != 201:
        print('Error creating task')
        return r

    params = r.json()
    task_id = params['id']
    task_update = { 'task' : {'column_id': column_id}}

    r2 = requests.put(url + '/tasks/' + str(task_id) + '.json', headers=headers_post, data=json.dumps(task_update))
    return r2

def store_token(api_filepath, token_filepath, token, password=None):

    use_encryption = 'False' 
    if password:
        use_encryption = 'True'

    with open(api_filepath, 'wt') as api_file:
        api_file.write('encryption=' + use_encryption)

    if password:
        cyphered = encrypt(password, token)
        with open(token_filepath, 'wb') as token_file:
            token_file.write(cyphered)
    else:
        with open(token_filepath, 'wt') as token_file:
            token_file.write(token)

    print('Config written to ' + api_filepath)
    print('Token written to ' + token_filepath)

def get_project_estimates():
    r = requests.get(url + '/projects/' + project + '/estimates.json', headers=headers_get)
    return r.json()

def authenticate():

    global input
    global token

    pybanery_dir = os.path.expanduser("~") + '/.pybanery'
    if not os.path.isdir(pybanery_dir):
        os.makedirs(pybanery_dir)

    api_filepath = pybanery_dir + '/config'

    if os.path.isfile(api_filepath):
        with open(api_filepath, 'rt') as api_file:
            encryption_type = api_file.readline().rstrip().split('=')[-1]
            if(encryption_type == 'False'):
                with open(pybanery_dir + '/token', 'rt') as token_file:
                    token = token_file.readline().rstrip()
                    validate_token(token)
            else:
                with open(pybanery_dir + '/token', 'rb') as token_file:

                    all_bytes = b''
                    new_data = token_file.read()

                    while new_data != b'':
                        all_bytes += new_data
                        new_data = token_file.read()

                is_valid = False
                while not is_valid:
                    is_valid = True
                    password = input('Enter your password: ')
                    try:
                        token = decrypt(password, all_bytes)
                    except DecryptionException:
                        print('Wrong password.')
                        is_valid = False

                validate_token(token)            
    else:
        print('Please input your kanbanery API Token. You can find it at https://kanbanery.com/user/api')
        print('Once it\'s correctly entered, you will have the choice to store it permantently')
        try: 
            input = raw_input
        except NameError: pass
        token = input("Enter your kanbanery API token: ")
        if validate_token(token):
            choice = ''
            while choice not in ['1', '2', '3']:        
                print('1. Store token permanently at ' + api_filepath + ' (it will be unencrypted)')
                print('2. Enter a password to associate with token')
                print('3. Just remember for this session')
                choice = input('Please choose one of the above methods: ')

            if choice ==  '1':
                store_token(api_filepath, pybanery_dir + '/token', token)
            elif choice == '2':
                password = input('Enter password: ')
                store_token(api_filepath, pybanery_dir +'/token', token, password)
        else:
            return False
    return True

