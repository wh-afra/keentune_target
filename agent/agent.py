""" 
KeenTune target main function.  

KeenTune-target running in tunning target environment with four main functions:

    1. Set parameters configuration: Apply the specified parameter configuration to this environment.
    2. Read parameters configuration: Read the parameter configuration of this environment.
    3. backup: Backup the parameter configuration of this environment to file.
    4. rollback: Rollback to parameter configuration defined in backup file.

"""
import tornado
import os
from agent.common.config import Config
from agent.controller.status import StatusHandler, AvaliableDomainHandler
from agent.controller.backup import BackupHandler
from agent.controller.rollback import RollbackHandler
from agent.controller.configure import ConfigureHandler
from agent.controller.detect import DetectHandler
from agent.controller.orig_conf import OriginalConfigurationHandler, backupOriginalConfiguration

def main():
    app = tornado.web.Application(handlers=[
        (r"/backup", BackupHandler),
        (r"/status", StatusHandler),
        (r"/rollback", RollbackHandler),
        (r"/configure", ConfigureHandler),
        (r"/detect", DetectHandler),
        (r"/original", OriginalConfigurationHandler),
        (r"/avaliable", AvaliableDomainHandler),
    ])
    app.listen(Config.AGENT_PORT)
    backupOriginalConfiguration()
    print("KeenTune-target running...")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        os._exit(0)