from target.common.config import Config

if Config.scene == 'default':
    from target.scene import default
    print("Active Scene: {}".format(Config.scene))
    ACTIVE_SCENE = default.DefaultScene()

else:
    print("[ERROR] unknown scene in {}, scene available: 'default', 'container', 'compiler', 'mysql'".format(Config.conf_file_path))
    exit(1)
