# Entourage

[![Ansible](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Ansible_Logo.png/64px-Ansible_Logo.png)](https://www.ansible.com/)

## Version
#### v1.1

## Overview

Ansible module for adding, overwriting and/or removing environment variables to/from the .bashrc of a specific user.

## Example

Add environment variable   
- skips if already exists with same value   
- overwrites if already exists with other value  
- inserts if doesn't exist
```yml
- name: Add environment variable
  entourage:
    user: myuser
    key: MY_VARIABLE
    value: my_value
    state: present
```

Removes environment variable  
- skips if doesn't exist  
- removes occurrence(s) if one or multiple exists
```yml
- name: Remove environment variable
  entourage:
    user: my_user
    key: MY_VARIABLE
    state: absent
```

## Changelog

#### v1.1
- sources the bashrc after altering it
- added support for root user
- added proper documentation
- added GPL3 License header

#### v1.0
- swapped out hard coded comparison with regex
- minor code cleanup

## Technical overview

At first, comparison was strict:  
MY_VAR=myvalue ---> worked  
MY_VAR = myvalue ---> didn't work  

Swapped out the old mechanism with regex, so every variety and number of spaces or tabs before/between/after keys and values works.