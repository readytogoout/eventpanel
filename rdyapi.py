import requests


class RdyApi:

    def __init__(self, hostname: str, api_key: str):
        self.hostname = hostname
        self.session = requests.Session()
        self.session.cookies.update(dict(
            session=api_key
        ))

    def create_user(self, username: str, password: str, group_id: str = "nogroup"):
        self.session.post(f'https://{self.hostname}/admin/users',
                          json=dict(
                              userName=username,
                              password=password,
                              groupId=group_id,
                              role='LOGGED_IN',  # hier könnte ihre rolle stehen
                          )).raise_for_status()

    def create_group(self, group_id: str, group_name: str):
        self.session.post(f'https://{self.hostname}/admin/groups',
                          json=dict(
                              groupId=group_id,
                              groupName=group_name,
                          )).raise_for_status()

    def get_users(self):
        res = self.session.get(f'https://{self.hostname}/admin/users')
        res.raise_for_status()
        return res.json()

    def get_groups(self):
        res = self.session.get(f'https://{self.hostname}/admin/groups')
        res.raise_for_status()
        return res.json()

    # if enabled all users of a group will spawn the npcs on the same location
    def set_sync_npcs(self, group_id: str, is_sync_npc: bool):
        res = self.session.patch(f'https://{self.hostname}/admin/groups', params=dict(groupId=group_id, isSyncNpcs=is_sync_npc))
        res.raise_for_status()
        return res.text

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
