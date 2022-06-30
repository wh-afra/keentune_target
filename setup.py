from setuptools import setup, find_packages

long_description = ""

setup(
    name        = "keentune-target",
    version     = "1.2.1",
    description = "KeenTune target unit",
    url         = "https://gitee.com/anolis/keentune_target",
    license     = "MulanPSLv2",
    packages    = find_packages(),
    package_data= {'agent': ['target.conf']},

    python_requires  = '>=3.6',
    long_description = long_description,
    
    classifiers = [
        "Environment:: KeenTune",
        "IntendedAudience :: Information Technology",
        "IntendedAudience :: System Administrators",
        "License :: OSI Approved :: MulanPSLv2",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "ProgrammingLanguage :: Python"
    ],
    data_files  = [
        ("/etc/keentune/target", ["LICENSE"]),
        ("/etc/keentune/conf", ["agent/target.conf"]),
    ],

    entry_points = {
        'console_scripts': ['keentune-target=agent.agent:main']
    }
)
