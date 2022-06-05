# import pysshconfig as psc

# import os

# def ssh_config(profile, host, user, identity_file, port='22'):

#     host_template = f"""
# Host {profile}
#     HostName {host}
#     User {user}
#     Port {port}
#     IdentityFile {identity_file}
#     """

#     # if os.path.exists(f"{os.getenv('HOME')}/.ssh/config"):
#     #     # check for position in ssh file and edit shit (update hostname )
#     #     pass
#     # else:
#     #     print("no")

#     # print(host_template)
#     with open(os.path.expanduser('~/.ssh/config')) as file:
#         ssh_config = psc.load(file)
    
#     print(ssh_config)

# def main():
#     ssh_config("blabla", "1.2.3.4", "MEEEE", "~/.ssh/something.pen")

# if __name__ == "__main__":
#     main()