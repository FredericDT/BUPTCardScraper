from webvpn import Webvpn
from card import Card
import config


if __name__ == '__main__':
    webvpn = Webvpn(
        username=config.webvpn_config['username'],
        password=config.webvpn_config['password']
    ).obtain_login_cookies()

    card = Card(
        webvpn.session,
        username=config.card_service_config['username'],
        password=config.card_service_config['password']
    ).obtain_login()

    r = card.obtain_comsume_information(account_type='0')

    print(r)