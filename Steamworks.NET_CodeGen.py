import sys
from SteamworksParser import steamworksparser
import interfaces
import constants
import enums
import structs
import typedefs

def main():
    if len(sys.argv) != 2:
        print("TODO: Usage Instructions")
        return

    steamworksparser.Settings.fake_gameserver_interfaces = True
    ___parser = steamworksparser.parse(sys.argv[1])

    interfaces.main(___parser)
    constants.main(___parser)
    enums.main(___parser)
    structs.main(___parser)
    typedefs.main(___parser)

if __name__ == "__main__":
    main()
