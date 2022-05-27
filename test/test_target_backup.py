import unittest
import requests
import json
from common import target_ip, target_port

class TestTargetBackup(unittest.TestCase):
    def setUp(self) -> None:
        self.proxies={"http": None, "https": None}
        url = "http://{}:{}/status".format(target_ip, target_port)
        re = requests.get(url, proxies=self.proxies)
        if re.status_code != 200:
            print("ERROR: Can't reach KeenTune-Target.")
            exit()
            
    def tearDown(self) -> None:
        url = "http://{}:{}/{}".format(target_ip, target_port, "rollback")
        data = {}
        headers = {"Content-Type": "application/json"}
        
        result = requests.post(url, data=json.dumps(data), headers=headers, proxies=self.proxies)
        self.assertEqual(result.status_code, 200)
        self.assertIn('"suc": true', result.text)

    def test_target_server_FUN_backup(self):
        url = "http://{}:{}/{}".format(target_ip, target_port, "backup")
        data = {
            "sysctl": {
                "fs.aio-max-nr": {"dtype": "read", "value": ""},
                "fs.file-max": {"dtype": "read", "value": ""}
                }
                }

        headers = {"Content-Type": "application/json"}
        
        result = requests.post(url, data=json.dumps(data), headers=headers, proxies=self.proxies)
        self.assertEqual(result.status_code, 200)
        self.assertIn(result.text, '{"suc": true, "msg": {"sysctl": "/var/keentune/backup/sysctl_backup.conf"}}')
