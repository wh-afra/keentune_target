""" 
KeenTune target main function.  

KeenTune-target running in tunning target environment with four main functions:

    1. Set parameters configuration: Apply the specified parameter configuration to this environment.
    2. Read parameters configuration: Read the parameter configuration of this environment.
    3. backup: Backup the parameter configuration of this environment to file.
    4. rollback: Rollback to parameter configuration defined in backup file.

"""

import tornado

from target.common.config import Config
from target.controller.status import StatusHandler
from target.controller.backup import BackupHandler
from target.controller.rollback import RollbackHandler
from target.controller.configure import ConfigureHandler
from target.controller.detect import DetectHandler


def main():
    app = tornado.web.Application(handlers=[
        (r"/backup", BackupHandler),
        (r"/status", StatusHandler),
        (r"/rollback", RollbackHandler),
        (r"/configure", ConfigureHandler),
        (r"/detect", DetectHandler),
    ])

    app.listen(Config.target_port)
    print("KeenTune-target running...")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
