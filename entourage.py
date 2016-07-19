#!/usr/bin/python

"""
Ansible module to manage environment variables in the ~/.bashrc.
Copyright(c) 2016, Gergo Nagy <@gerynix>

This module is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This module is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

DOCUMENTATION = '''
---
module: entourage
short_description: Module through which you can manage environment variables in the C(~/.bashrc).
description:
    - Ansible module for adding, overwriting and/or removing environment variables to/from the C(~/.bashrc).
    - You can specify any user, even the root user.
version_added: "1.1"
options:
  user:
    description:
      - The user for which you would like to add/overwrite/delete an environment variable to/from the C(~/.bashrc).
    required: true
    default: null
  key:
    description:
      - The name of the environment variable to be added/overridden/removed.
    required: true
    default: null
  value:
    description:
      - The value of the environment variable to be added.
    required: true
    default: null
  state:
    description:
      - I(present) to add an environment variable, I(absent) to remove it.
    choices: [ "present", "absent" ]
    required: false
    default: present
author: "Gergo Nagy (@gerynix)"
'''

EXAMPLES = '''
# Add environment variable
# - skips if already exists with same value
# - overwrites if already exists with other value
# - inserts if doesn't exist
- name: Add environment variable
  entourage:
    user: myuser
    key: MY_VARIABLE
    value: my_value
    state: present

# Removes environment variable
# - skips if doesn't exist
# - removes occurrence(s) if one or multiple exists
- name: Remove environment variable
  entourage:
    user: my_user
    key: MY_VARIABLE
    value: not_used
    state: absent
'''

from ansible.module_utils.basic import *

import re
import subprocess

def entourage_present(data, bashrc_path):
    new_variable_def_regex = "(|[ \\t]+)\\b" + data['key'] + "\\b(|[ \\t]+)=.*"
    new_variable_regex = "(|[ \\t]+)\\b" + data['key'] + "\\b(|[ \\t]+)=(|[ \\t]+)\\b" + data['value'] + "\\b(|[ \\t]+)"
    new_variable_def_pattern = re.compile(new_variable_def_regex)
    new_variable_pattern = re.compile(new_variable_regex)

    new_variable = data['key'] + "=" + data['value'] + "\n"

    present = False

    with open(bashrc_path) as bashrc:
        for line in bashrc:
            if new_variable_def_pattern.match(line):
                # if variable defined
                present = True
                if new_variable_pattern.match(line):
                    # if variable is the same, do nothing
                    result = {"info": "Variable is in bashrc"}
                    return False, False, result
                else:
                    # if variable isn't the same, overwrite
                    replace_in_file(bashrc_path, line, new_variable)
                    subprocess.call('source ' + bashrc_path, shell=True)
                    result = {"info": "Variable was in bashrc", "old_var": line, "new_var": new_variable}
                    return False, False, result

    if not present:
        with open(bashrc_path, "a") as bashrc:
            bashrc.write(new_variable)
    subprocess.call('source ' + bashrc_path, shell=True)
    result = {"info": "Variable inserted into bashrc"}
    return False, True, result



def entourage_absent(data, bashrc_path):
    new_variable_def_regex = "(|[ \\t]+)\\b" + data['key'] + "\\b(|[ \\t]+)=.*"
    new_variable_def_pattern = re.compile(new_variable_def_regex)

    num = 0

    with open(bashrc_path) as bashrc:
        for line in bashrc:
            # if variable defined
            if new_variable_def_pattern.match(line):
                replace_in_file(bashrc_path, line, "\n")
                subprocess.call('source ' + bashrc_path, shell=True)
                num += 1

    if num == 1:
        result = {"info": "Variable removed from bashrc"}
        return False, True, result
    if num > 1:
        result = {"info": "Variables removed from bashrc", "instances": num}
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

    if module.params['user'] == "root":
        bashrc_path = "/root/.bashrc"
    else:
        bashrc_path = "/home/" + module.params['user'] + "/.bashrc"

    is_error, has_changed, result = choice_map.get(
            module.params['state'])(module.params, bashrc_path)

    if not is_error:
        module.exit_json(changed=has_changed, meta=result)
    else:
        module.fail_json(msg="Error while handling environment variable", meta=result)

main()