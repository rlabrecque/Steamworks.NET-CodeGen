import os
import sys
from SteamworksParser import steamworksparser

g_FlagEnums = (
    # ISteamFriends
    "EPersonaChange",
    "EFriendFlags",

    #ISteamHTMLSurface
    "EHTMLKeyModifiers",

    #ISteamInventory
    "ESteamItemFlags",

    # ISteamMatchmaking
    "EChatMemberStateChange",

    # ISteamRemoteStorage
    "ERemoteStoragePlatform",

    # ISteamUGC
    "EItemState",

    # SteamClientPublic
    "EAppOwnershipFlags",
    "EAppType",
    "EChatSteamIDInstanceFlags",
    "EMarketingMessageFlags",
)

g_SkippedEnums = (
    # TODO: Why?
    "EGameIDType",
)

g_ValueConversionDict = {
    "0xffffffff": "-1",
    "0x80000000": "-2147483647",
    "k_unSteamAccountInstanceMask": "Constants.k_unSteamAccountInstanceMask",
}

def main(parser):
    try:
        os.makedirs("autogen/")
    except OSError:
        pass

    lines = []
    for f in parser.files:
        for enum in f.enums:
            if enum.name in g_SkippedEnums:
                continue

            for comment in enum.c.rawprecomments:
                if type(comment) is steamworksparser.BlankLine:
                    continue
                lines.append("\t" + comment)

            if enum.name in g_FlagEnums:
                lines.append("\t[Flags]")

            lines.append("\tpublic enum " + enum.name + " : int {")

            for field in enum.fields:
                for comment in field.c.rawprecomments:
                    if type(comment) is steamworksparser.BlankLine:
                        lines.append("")
                    else:
                        lines.append("\t" + comment)
                line = "\t\t" + field.name
                if field.value:
                    if "<<" in field.value and enum.name not in g_FlagEnums:
                        print("[WARNING] Enum is contains "<<" but is not marked as a flag! - " + enum.name)

                    if field.value == "=" or field.value == "|":
                        line += " "
                    else:
                        line += field.prespacing + "=" + field.postspacing

                    value = field.value
                    for substring in g_ValueConversionDict:
                        if substring in field.value:
                            value = value.replace(substring, g_ValueConversionDict[substring], 1)
                            break
                            
                    line += value
                if field.c.rawlinecomment:
                    line += field.c.rawlinecomment
                lines.append(line)

            for comment in enum.endcomments.rawprecomments:
                if type(comment) is steamworksparser.BlankLine:
                    lines.append("")
                else:
                    lines.append("\t" + comment)

            lines.append("\t}")
            lines.append("")

    with open("autogen/SteamEnums.cs", "wb") as out:
        with open("header.txt", "r") as f:
            out.write(f.read())
        for line in lines:
            out.write(line + "\n")
        out.write("}\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("TODO: Usage Instructions")
        exit()

    steamworksparser.Settings.fake_gameserver_interfaces = True
    main(steamworksparser.parse(sys.argv[1]))