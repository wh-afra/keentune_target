import re  
import os
from datetime import datetime

""" warpping the KeenTune module keentune-target

This script will
1. Check the version number in *.spec and setup.py
2. Check the date of changelog in *.spec
3. Pick necessary file to a folder named as keentune-target-{version}
4. Pack the folder to .tar.gz
5. Get a copy of *.spec.

You can run this script in any position as 

python3 /path/in/your/environment/packup.py
"""

source_dir = os.path.split(os.path.realpath(__file__))[0]

def dateCheck(spec):
    date_items = re.findall(r"\* (\w+) (\w+) (\d+) (\d+) .*",spec)
    for date in date_items:
        _date = datetime.strptime("{} {} {}".format(date[3], date[1], date[2]),"%Y %b %d")
        if not _date.strftime("%a") == date[0]:
            raise Exception("week error:'{}', should be '{}'".format(date, _date.strftime("%a")))


def warppingCheck():
    with open(os.path.join(source_dir,"keentune-target.spec"),'r') as f:
        spec = f.read()
        version_in_spec = re.search("Version:        ([\d.]+)\n",spec).group(1)
        release_in_spec = re.search("define anolis_release (\d)\n",spec).group(1)
        print("Get version: {}-{}".format(version_in_spec, release_in_spec))
        dateCheck(spec)

        if re.search(" - {}-{}".format(version_in_spec, release_in_spec), spec):
            print("[OK] check the version of changelog at keentune-target.spec.")
        else:
            print("[Failed] wrong version number in changelog at keentune-target.spec.")
            return

    with open(os.path.join(source_dir,"setup.py"), 'r') as f:
        script = f.read()
        if re.search('version     = "{}",'.format(version_in_spec),script):
            print("[OK] check the version of setup.py.")
        else:
            print("[Failed] wrong version number in setup.py.")
            return

    print("Start wrap up of keentune-target-{}-{}".format(version_in_spec, release_in_spec))
    return version_in_spec, release_in_spec

if __name__ == "__main__":
    version_in_spec, _ = warppingCheck()
    if os.path.exists("keentune-target-{}".format(version_in_spec)):
        os.system("rm -rf keentune-target-{}".format(version_in_spec))
    
    os.system("mkdir keentune-target-{}".format(version_in_spec))

    os.system("cp -r {} keentune-target-{}".format(os.path.join(source_dir,"agent"), version_in_spec))
    os.system("cp -r {} keentune-target-{}".format(os.path.join(source_dir,"keentune-target.service"), version_in_spec))
    os.system("cp -r {} keentune-target-{}".format(os.path.join(source_dir,"LICENSE"), version_in_spec))
    os.system("cp -r {} keentune-target-{}".format(os.path.join(source_dir,"README.md"), version_in_spec))
    os.system("cp -r {} keentune-target-{}".format(os.path.join(source_dir,"requirements.txt"), version_in_spec))
    os.system("cp -r {} keentune-target-{}".format(os.path.join(source_dir,"setup.py"), version_in_spec))

    os.system("tar -cvzf keentune-target-{}.tar.gz --exclude=**/__pycache__ keentune-target-{}".format(
        version_in_spec, version_in_spec))

    if os.path.exists("keentune-target-{}".format(version_in_spec)):
        os.system("rm -rf keentune-target-{}".format(version_in_spec))

    os.system("cp {} ./".format(os.path.join(source_dir, "keentune-target.spec")))