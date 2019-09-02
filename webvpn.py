import requests


class Webvpn:
    def __init__(self, username=None, password=None):
        self._username = username
        self._password = password
        self.session = None

    def obtain_init_session(self):
        self.session = requests.Session()
        r = self.session.get('https://vpn.bupt.edu.cn/global-protect/login.esp')
        assert r.cookies
        return self

    def obtain_login_cookies(self):
        assert self._username is not None and self._password is not None

        self.obtain_init_session()
        assert self.session

        self.session.post('https://vpn.bupt.edu.cn/global-protect/login.esp',
                          data={
                              'prot': 'https:',
                              'server': 'vpn.bupt.edu.cn',
                              'inputStr': '',
                              'action': 'getsoftware',
                              'user': self._username,
                              'passwd': self._password,
                              'ok': 'Log In'
                          })

        assert self.is_login_success(), 'Webvpn credential invalid'

        return self

    def is_login_success(self):
        if self.session is not None:
            if self.session.cookies is not None:
                return 'GP_SESSION_CK' in self.session.cookies
        return False

    def __exit__(self, *args):
        if self.session:
            self.session.close()
