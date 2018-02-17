import os
import subprocess
import json

class Runner(object):

    def __init__(self,
                 playbooks,
                 tags,  # must have
                 extra_vars,
                 hostnames='127.0.0.1',
                 connection='local',  # smart|ssh|local
                 private_key_file='',
                 become_pass='',
                 vault_pass='',
                 verbosity=0,
                 debug=False):
        self.debug = debug
        self.private_key_file = private_key_file
        self.become = True
        self.become_method = 'sudo'
        self.become_user = 'root'
        self.become_pass = become_pass
        self.connection = connection
        self.tags = tags
        self.extra_vars = extra_vars
        self.playbooks = playbooks
        if verbosity==0:
            self.verbosity=''
        else:
            self.verbosity = '-' + verbosity*'v'
        self.vault_pass = vault_pass
    

        # Become Pass Needed if not logging in as user root
        passwords = {'become_pass': self.become_pass}

        # Playbook to run. Assumes it is
        # local and relative to this python file
        # in "../../../playbooks" directory.
        dirname = os.path.dirname(__file__) or '.'
        pb_rel_dir = '../../../playbooks'
        playbook_path = os.path.join(dirname, pb_rel_dir)
        self.module_path = os.path.join(playbook_path, 'library')
        pbs = [os.path.join(playbook_path, pb) for pb in self.playbooks]
        
        self.callme = [
            'ansible-playbook',
            ','.join(pbs),
            '-c',
            self.connection,
            self.verbosity 
        ]
        if self.tags:
            self.callme += ['--tags', tags]
        if self.extra_vars:
            evars = json.dumps(self.extra_vars)
            self.callme += ['--extra-vars', '"%s"' %(evars)]
        if self.module_path:
            self.callme += ['--module-path',self.module_path]

    def run(self):
        if self.debug:
            print("ansbile cmd: ", ' '.join(self.callme))

        return_code = subprocess.call(' '.join(self.callme), shell=True)
        return True if return_code == 0 else False

