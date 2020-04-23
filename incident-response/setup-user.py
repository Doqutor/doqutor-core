import os
import json

dirname = os.path.abspath(__file__)
base, curr_dir = os.path.split(dirname)
base, curr_dir = os.path.split(base)
config_user = os.path.join(base, 'js-infra')


def get_user_details():
    global prefix, f, users, user
    prefix = None
    with open(f'{config_user}/config.json') as f:
        prefix = json.load(f)['prefix']
    try:
        if prefix is not None:
            # write all users in json file
            os.system('aws iam list-users > users.json')

            # read from json file
            f = open('users.json')
            # returns JSON object as
            users = json.load(f)['Users']
            # find users
            test_user_username = None
            for user in users:
                if prefix in user['UserName']:
                    test_user_username = user['UserName']
                    break

            if test_user_username is not None:
                os.system(f'aws iam create-access-key --user-name {test_user_username} > user_key.json')
                print('Open user_key.json file in the current directory and fill in the details below')
                os.system('aws configure')
            else:
                print('test user not found')


    except:
        print('something wrong happened')
    finally:
        f.close()
        if os.path.exists("users.json"):
            os.remove("users.json")
        if os.path.exists("user_key.json"):
            os.remove("user_key.json")


if __name__ == '__main__':
    get_user_details()
