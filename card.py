import requests
from bs4 import BeautifulSoup


def extract_form_from_content(content):
    soup = BeautifulSoup(content, features="html.parser")
    form = {}
    for i in soup.form.find_all('input'):
        form[i.attrs['name']] = i.attrs['value'] if 'value' in i.attrs else None
    return form


class Card:
    def __init__(self, session=None, username=None, password=None):
        assert session
        assert username is not None and password is not None

        self.session = session
        self._username = username
        self._password = password

    def __exit__(self, *args):
        if self.session:
            self.session.close()

    def obtain_login_form(self):
        response = self.session.get('https://vpn.bupt.edu.cn/http/10.3.255.131/Login.aspx')
        form = extract_form_from_content(response.content)
        return form

    def obtain_login(self):
        form = self.obtain_login_form()
        form['txtUserName'] = self._username
        form['txtPassword'] = self._password
        form['__EVENTTARGET'] = 'btnLogin'

        response = self.session.post('https://vpn.bupt.edu.cn/http/10.3.255.131/Login.aspx',
                                     data=form
                                     )

        assert response.url[-10:] == 'Index.aspx', 'Card credential invalid'

        return self

    def obtain_consume_form(self):
        response = self.session.get('https://vpn.bupt.edu.cn/http/10.3.255.131/User/ConsumeInfo.aspx')
        form = extract_form_from_content(response.content)
        return form

    '''
    account_type = '0' 主钱包
    
    [
        [
            {'key': '操作时间', 'value': '2000/1/1 10:00:00'}, 
            {'key': '科目描述', 'value': '商场购物'},
            {'key': '钱包交易金额', 'value': '4.50'}, 
            {'key': '钱包余额', 'value': '1.10'}, 
            {'key': '操作员', 'value': '虚拟职员'},
        {'key': '工作站', 'value': '学苑超市采集工作站'}, 
            {'key': '终端名称', 'value': '学 苑超市pos机3#'}
        ]
    ]
    
    '''
    def obtain_comsume_information(self, start_date=None, end_date=None, account_type=None):
        form = self.obtain_consume_form()

        form['__EVENTTARGET'] = ''
        form['__EVENTARGUMENT'] = ''

        if start_date:
            form['ctl00$ContentPlaceHolder1$txtStartDate'] = start_date
        if end_date:
            form['ctl00$ContentPlaceHolder1$txtEndDate'] = end_date
        if account_type:
            form['ctl00$ContentPlaceHolder1$rbtnType'] = account_type

        response = self.session.post('https://vpn.bupt.edu.cn/http/10.3.255.131/User/ConsumeInfo.aspx',
                                     data=form
                                     )

        soup = BeautifulSoup(response.content, features="html.parser")
        table_headers = []
        table = []
        for i in soup.find(id='ContentPlaceHolder1_gridView').find_all('tr'):
            ths = i.find_all('th')
            if len(ths) > 0:
                for j in ths:
                    tha = j.a
                    if tha:
                        j = tha
                    table_headers += j.contents
            tds = i.find_all('td')
            if len(tds) > 0:
                j = 0
                table_data = []
                for k in tds:
                    span = k.find('span')
                    if span:
                        k = span
                    if len(k.contents) > 0:
                        if k.contents[0] == '\xa0' or k.contents[0].strip() is '':
                            break
                        table_data += [{
                            'key': table_headers[j],
                            'value': k.contents[0]
                        }]
                    else:
                        table_data += [{
                            'key': table_headers[j],
                            'value': ''
                        }]
                    j += 1
                if len(table_data) == len(table_headers):
                    table += [table_data]
        # TODO: fit multiple tables

        return table
