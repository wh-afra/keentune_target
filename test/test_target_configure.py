import json
import requests
import unittest


class TestTargetConfigure(unittest.TestCase):
    def setUp(self) -> None:
        self.proxies={"http": None, "https": None}
        url = "http://{}:{}/status".format("localhost", "9873")
        re = requests.get(url, proxies=self.proxies)
        if re.status_code != 200:
            print("ERROR: Can't reach KeenTune-Target.")
            exit()

    def tearDown(self) -> None:
        pass

    def test_target_server_FUN_configure(self):
        url = "http://{}:{}/{}".format("localhost", "9873", "configure")
        data_base = {
            "data": {
                "sysctl": {
                    "fs.aio-max-nr": {"dtype": "read", "value": ""},
                    "fs.file-max": {"dtype": "read", "value": ""}
                    }
                    }, 
                    "resp_ip": "localhost", 
                    "resp_port": "9871",
                    "target_id": 1,
                    "readonly": True
                    }

        headers = {"Content-Type": "application/json"}
        
        result = requests.post(url, data=json.dumps(data_base), headers=headers, proxies=self.proxies)
        self.assertEqual(result.status_code, 200)
        self.assertIn('"suc": true', result.text)
        
        data_set = {
            "data": {
                "sysctl": {
                    "fs.aio-max-nr": {"dtype": "read", "value": "102400"},
                    "fs.file-max": {"dtype": "read", "value": ""}
                    }
                    }, 
                    "resp_ip": "localhost", 
                    "resp_port": "9871",
                    "target_id": 1,
                    "readonly": True
                    }
        result = requests.post(url, data=json.dumps(data_set), headers=headers, proxies=self.proxies)
        self.assertEqual(result.status_code, 200)
        self.assertIn('"suc": true', result.text)
