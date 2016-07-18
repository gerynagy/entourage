#!/usr/bin/python
#@author Gery Nagy<gergo.nagy@endava.com>

DOCUMENTATION = '''
---
module: entourage
short_description: Adds, removes, overwrites environment variables in bashrc
'''

EXAMPLES = '''
- name: Add environment variable
  entourage:
    user: myuser
    key: MY_VARIABLE
    value: my_value
    state: present

- name: Remove environment variable
  entourage:
    user: my_user
    key: MY_VARIABLE
    value: not_used
    state: absent
'''

from ansible.module_utils.basic import *
import re

def entourage_present(data):
    bashrc_path = "/home/" + data['user'] + "/.bashrc"

    new_variable_definition = data['key'] + "="
    new_variable = new_variable_definition + data['value'] + "\n"

    present = False

    with open(bashrc_path) as bashrc:
        for line in bashrc:
            if new_variable_definition in line:
                # if variable defined
                present = True
                if new_variable == line:
                    # if variable is the same, do nothing
                    result = {"info": "Variable is in bashrc"}
                    return False, False, result
                else:
                    # if variable isn't the same, overwrite
                    replace_in_file(bashrc_path, line, new_variable)
                    result = {"info": "Variable was in bashrc", "old_var": line, "new_var": new_variable}
                    return False, False, result

    if not present:
        with open(bashrc_path, "a") as bashrc:
            bashrc.write(new_variable)
    result = {"info": "Variable inserted into bashrc"}
    return False, True, result



def entourage_absent(data):
    bashrc_path = "/home/" + data['user'] + "/.bashrc"

    new_variable_definition = data['key'] + "="

    with open(bashrc_path) as bashrc:
        for line in bashrc:
            if new_variable_definition in line:
                # if variable defined
                replace_in_file(bashrc_path, line, "\n")
                result = {"info": "Variable removed from bashrc"}
                return False, True, result

    result = {"info": "Variable was absent in bashrc"}
    return False, False, result


def replace_in_file(path, pattern, substitution):
    file_handle = open(path, "r")
    file_string = file_handle.read()
    file_handle.close()
    file_string = re.sub(pattern, substitution, file_string)
    file_handle = open(path, "w")
    file_handle.write(file_string)
    file_handle.close()

def main():

    fields = {
        "user": {"required": True, "type": "str"},
        "key": {"required": True, "type": "str"},
        "value": {"required": True, "type": "str"},
        "state": {
            "default": "present",
            "choices": ['present', 'absent'],
            "type": "str"
        }
    }

    choice_map = {
        "present": entourage_present,
        "absent": entourage_absent
    }

    module = AnsibleModule(argument_spec=fields)
    is_error, has_changed, result = choice_map.get(
            module.params['state'])(module.params)

    if not is_error:
        module.exit_json(changed=has_changed, meta=result)
    else:
        module.fail_json(msg="Error handling environment variable", meta=result)


if __name__ == '__main__':
    main()