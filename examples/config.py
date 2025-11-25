import nest

def preBuild():
    print("hello")

def postBuild():
    pass

config = nest.newConfig()

config.hostname = "vaelixd-pc"
config.kernels = ["linux-zen", "linux", "linux-lts"]
config.bootloader = "refind"
config.initramfsGenerator = "dracut"
config.preBuild = preBuild
config.postBuild = postBuild

vaelixd = nest.User(
    fullName="vaelixd",
    userName="vaelixd",
    homeDir="/home/vaelixd",
    manageHome=True,
    groups=["vaelixd", "wheel"]
)

config.users = [
    vaelixd
]

nest.returnConfig(config)
