import os
import subprocess
from tempfile import NamedTemporaryFile
import json

class Options(object):
    """
    Options class to replace Ansible OptParser
    """

    def __init__(self, verbosity=None,
                 inventory=None,
                 listhosts=None,
                 subset=None,
                 module_paths=None,
                 extra_vars=None,
                 forks=None,
                 ask_vault_pass=None,
                 vault_password_files=None,
                 new_vault_password_file=None,
                 output_file=None,
                 tags=None,
                 skip_tags=[],
                 one_line=None,
                 tree=None,
                 ask_sudo_pass=None,
                 ask_su_pass=None,
                 sudo=None,
                 sudo_user=None,
                 become=None,
                 become_method=None,
                 become_user=None,
                 become_ask_pass=None,
                 ask_pass=None,
                 private_key_file=None,
                 remote_user=None,
                 connection=None,
                 timeout=None,
                 ssh_common_args=None,
                 sftp_extra_args=None,
                 scp_extra_args=None,
                 ssh_extra_args=None,
                 poll_interval=None,
                 seconds=None,
                 check=None,
                 syntax=None,
                 diff=None,
                 force_handlers=None,
                 flush_cache=None,
                 listtasks=None,
                 listtags=[],
                 module_path=None):
        self.verbosity = verbosity
        self.inventory = inventory
        self.listhosts = listhosts
        self.subset = subset
        self.module_paths = module_paths
        self.extra_vars = extra_vars
        self.forks = forks
        self.ask_vault_pass = ask_vault_pass
        self.vault_password_files = vault_password_files
        self.new_vault_password_file = new_vault_password_file
        self.output_file = output_file
        self.tags = tags
        self.skip_tags = skip_tags
        self.one_line = one_line
        self.tree = tree
        self.ask_sudo_pass = ask_sudo_pass
        self.ask_su_pass = ask_su_pass
        self.sudo = sudo
        self.sudo_user = sudo_user
        self.become = become
        self.become_method = become_method
        self.become_user = become_user
        self.become_ask_pass = become_ask_pass
        self.ask_pass = ask_pass
        self.private_key_file = private_key_file
        self.remote_user = remote_user
        self.connection = connection
        self.timeout = timeout
        self.ssh_common_args = ssh_common_args
        self.sftp_extra_args = sftp_extra_args
        self.scp_extra_args = scp_extra_args
        self.ssh_extra_args = ssh_extra_args
        self.poll_interval = poll_interval
        self.seconds = seconds
        self.check = check
        self.syntax = syntax
        self.diff = diff
        self.force_handlers = force_handlers
        self.flush_cache = flush_cache
        self.listtasks = listtasks
        self.listtags = listtags
        self.module_path = module_path


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
        self.hostnames = hostnames
        if verbosity==0:
            self.verbosity=''
        else:
            self.verbosity = '-' + verbosity*'v'
        self.vault_pass = vault_pass
    

        # Become Pass Needed if not logging in as user root
        passwords = {'become_pass': self.become_pass}

        # Parse hosts, I haven't found a good way to
        # pass hosts in without using a parsed template :(
        # (Maybe you know how?)
        self.hosts = NamedTemporaryFile(delete=False, mode='wt')
        self.hosts.write("""[run_hosts]\n%s""" % hostnames)
        self.hosts.close()

        # This was my attempt to pass in hosts directly.
        #
        # Also Note: In py2.7, "isinstance(foo, str)" is valid for
        #            latin chars only. Luckily, hostnames are
        #            ascii-only, which overlaps latin charset

        # Playbook to run. Assumes it is
        # local and relative to this python file
        # in "../../../playbooks" directory.
        dirname = os.path.dirname(__file__) or '.'
        pb_rel_dir = '../../../playbooks'
        playbook_path = os.path.join(dirname, pb_rel_dir)
        self.module_path = os.path.join(playbook_path, 'library')

        # os.environ['ANSIBLE_CONFIG'] = os.path.abspath(os.path.dirname(__file__))
        pbs = [os.path.join(playbook_path, pb) for pb in self.playbooks]


        # TODO: so here we construct a CLI line.
        # For whatever reason, api is not taking account for `tags`!!
        self.callme = [
            'ansible-playbook',
            '-i',
            self.hosts.name,
            ','.join(pbs),
            '-c',
            self.connection,
            self.verbosity 
        ]
        if self.tags:
            self.callme += ['--tags', tags]
        if self.extra_vars:
            self.extra_vars_file = os.path.join(os.getenv('HOME'),"extra_vars.json") 
            with open(self.extra_vars_file, "wt") as fp:
                json.dump(extra_vars, fp)
            self.callme += ['--extra-vars', '"@%s"' % (self.extra_vars_file)]
        if self.module_path:
            self.callme += ['--module-path',self.module_path]

    def run(self):
        if self.debug:
            print "ansbile cmd: ", ' '.join(self.callme)

        return_code = subprocess.call(' '.join(self.callme), shell=True)
        #os.remove(self.extra_vars_file)
        os.remove(self.hosts.name)
        return True if return_code == 0 else False

