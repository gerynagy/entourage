# Automated WP development machine setup

[![Ansible](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Ansible_Logo.png/64px-Ansible_Logo.png)](https://www.ansible.com/)

## Overview

Ansible module for adding, overwriting and/or removing environment variables to/from the .bashrc

## Example

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

## Technical overview

At first, comparison was strict:
MY_VAR=myvalue                      -> worked
MY_VAR = myvalue                    -> didn't work

Now, regex happened, so even:
         MY_VAR      =    myvalue   -> works