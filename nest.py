from dataclasses import asdict, dataclass, field
from inspect import getsource
from os import getenv, mkdir, path
from types import FunctionType
from typing import List, Optional

@dataclass
class User:
    homeDir: str
    fullName: str
    userName: str
    manageHome: bool = False
    groups: List[str] = field(default_factory=list)

@dataclass
class NestConfig:
    hostname: str
    kernels: List[str] = field(default_factory=list)
    users: List[User] = field(default_factory=list)
    bootloader: str = "limine"
    initramfsGenerator: str = "booster"
    preBuild: Optional[FunctionType] = None
    postBuild: Optional[FunctionType] = None

os_info = {}
nest_gen_root = getenv("NEST_GEN_ROOT") or ""
nest_autogen = nest_gen_root + "autogen/" if nest_gen_root else ""

def newConfig() -> NestConfig:
    with open("/etc/os-release", "r") as os_release:
        for line in os_release:
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, _, value = line.partition("=")
            value = value.strip("'\"")
            os_info[key.lower()] = value

    config = NestConfig(
        hostname=os_info["id"],
        kernels=["linux"],
    )

    return config

def returnConfig(config: NestConfig):
    usersConfig = config.users
    configDict = asdict(config)
    scsvConfig = ""

    for key in configDict:
        if key == "users":
            value = __checkValue(key, usersConfig)
        else:
            value = __checkValue(key, configDict[key])

        if value == False:
            continue
        if type(value) != str:
            return 4
        scsvConfig += f"{key},{value}\n"

    print(scsvConfig)

def __checkValue(key: str, value):
    if key == "hostname":
        return str(value).replace(" ", "-").lower()
    elif key == "preBuild" or key == "postBuild":
        if value != None:
            buildFunc = [getsource(value), value.__name__]
            __generateBuildFiles(buildFunc, key)

        return False
    elif type(value) == list:
        if key == "kernels":
            return str.join(",", value)
        elif key == "users":
            __generateUserConfig(value)
            return False
    else:
        return value

def __generateBuildFiles(buildFunc: list[str], buildType: str):
    if not path.exists(nest_autogen) and nest_autogen != "":
        mkdir(nest_autogen)

    with open(f"{nest_autogen}{buildType}.py", "w") as file:
            file.writelines([buildFunc[0] + "\n", buildFunc[1] + "()"])

def __generateUserConfig(users: List[User]):
    usersSCSV = """#@valuePrecedence,false
#@strictMode,false

"""

    for user in users:
        user.userName = user.userName if user.userName else user.fullName.lower()
        user.fullName = user.fullName if user.fullName else user.userName
        user.homeDir = user.homeDir if user.homeDir else f"/home/{user.userName}"

        if not user.userName in user.groups:
            user.groups = [user.userName] + user.groups

        usersSCSV += f"""|{user.userName},fullName,{user.fullName}
,homeDir,{user.homeDir}
,manageHome,{str(user.manageHome).lower()}
,groups,{str.join(",", user.groups)}

"""
 
    if not path.exists(nest_autogen) and nest_autogen != "":
        mkdir(nest_autogen)

    with open(f"{nest_autogen}users.scsv", "w") as file:
        file.write(usersSCSV)
