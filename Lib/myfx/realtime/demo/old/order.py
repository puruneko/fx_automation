import queue
import http.client as httpClient

class Order(object):
    def __init__(self, domain, access_token, account_id):
        self.domain = domain
        self.access_token = access_token
        self.account_id = account_id
        self.conn = self.obtain_connection()

    def obtain_connection(self):
        return httpClient.HTTPSConnection(self.domain)

    def send_order(self, event):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer " + self.access_token
        }
        params = urllib.urlencode({
            "instrument" : event.instrument,
            "units" : event.units,
            "type" : event.order_type,
            "side" : event.side
        })
        self.conn.request(
            "POST",
            "/v1/accounts/{0:s}/orders".format(str(self.account_id)),
            params, headers
        )
        response = self.conn.getresponse().read()
        with open("history_event.txt", "a") as file:
            file.write("@order\t{}\n".format(response))
