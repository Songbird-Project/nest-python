from dataclasses import asdict, dataclass

@dataclass
class NestConfig:
    hostname: str

def newConfig() -> NestConfig:
    os_info = {}
    config = NestConfig(
        hostname=""
    )

    with open("/etc/os-release", "r") as os_release:
        for line in os_release:
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, _, value = line.partition("=")
            value = value.strip("'\"")
            os_info[key.lower()] = value

    config.hostname = os_info["id"]

    return config

def returnConfig(config: NestConfig):
    configDict = asdict(config)
    scsvConfig = ""

    for key in configDict:
        scsvConfig += key + "," + __checkValue(key, configDict[key]) + "\n"

    print(scsvConfig)

def __checkValue(key: str, value):
    if key == "hostname":
        return str(value).replace(" ", "-")
    else:
        return value
