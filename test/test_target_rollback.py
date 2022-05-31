import json
import requests
import unittest


class TestTargetRollback(unittest.TestCase):
    def setUp(self) -> None:
        self.proxies={"http": None, "https": None}
        url = "http://{}:{}/status".format("localhost", "9873")
        re = requests.get(url, proxies=self.proxies)
        if re.status_code != 200:
            print("ERROR: Can't reach KeenTune-Target.")
            exit()
            
        url = "http://{}:{}/{}".format("localhost", "9873", "backup")
        data = {
            "sysctl": {
                "fs.aio-max-nr": {"dtype": "read", "value": ""},
                "fs.file-max": {"dtype": "read", "value": ""}
                }
                }

        headers = {"Content-Type": "application/json"}
        
        result = requests.post(url, data=json.dumps(data), headers=headers, proxies=self.proxies)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.text, '{"suc": true, "msg": {"sysctl": "/var/keentune/backup/sysctl_backup.conf"}}')
        
    def tearDown(self) -> None:
        pass

    def test_target_server_FUN_rollback(self):
        url = "http://{}:{}/{}".format("localhost", "9873", "rollback")
        data = {}
        headers = {"Content-Type": "application/json"}
        result = requests.post(url, data=json.dumps(data), headers=headers, proxies=self.proxies)
        self.assertEqual(result.status_code, 200)
        self.assertIn('"suc": true', result.text)
