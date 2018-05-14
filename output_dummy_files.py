import os
import sys

"""
Outputs empty files when Valve removes interfaces so that people upgrading don't have old bad data.
"""
def main():
    list_of_files = (
        ("autogen", "isteamunifiedmessages.cs"),
        ("types/SteamUnifiedMessages", "ClientUnifiedMessageHandle.cs"),
        ("types/SteamClient", "SteamAPI_PostAPIResultInProcess_t.cs"),
    )

    for f in list_of_files:
        try:
            os.makedirs(f[0])
        except OSError:
            pass

        with open(os.path.join(f[0], f[1]), "wb") as out:
            with open("templates/header.txt", "r") as f:
                out.write(bytes(f.read(), "utf-8"))
            out.write(bytes("#endif // !DISABLESTEAMWORKS\n", "utf-8"))
            out.write(bytes("\n", "utf-8"))
            out.write(bytes("// This file is no longer needed.\n", "utf-8"))

if __name__ == "__main__":
    main()
