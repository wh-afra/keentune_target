from setuptools import setup, find_packages

long_description = ""

setup(
    name = "keentune-target",
    version = "1.0.0",
    description = "KeenTune target unit",
    long_description = long_description,
    url = "https://codeup.openanolis.cn/codeup/keentune/keentune_target",
    license = "Apache License",
    classifiers = [
        "Environment:: KeenTune",
        "IntendedAudience :: Information Technology",
        "IntendedAudience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "ProgrammingLanguage :: Python"
    ],

    packages = find_packages(),
    package_data={'target': ['target.conf']},
    
    data_files = [
        ("/etc/keentune/",["LICENSE"]),
        ("/etc/keentune/conf", ["target/target.conf"]),
    ],
)
