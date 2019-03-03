import os
import sys
from SteamworksParser import steamworksparser

g_TypeDict = {
    # Not a bug... But, it's a giant hack.
    # The issue is that most of these are used as the MarshalAs SizeConst in C# amongst other things and C# wont auto convert them.
    "uint32": "int",
    "unsigned int": "int",

    "uint64": "ulong",
}

g_SkippedDefines = (
    "VALVE_COMPILE_TIME_ASSERT(",
    "REFERENCE(arg)",
    "STEAM_CALLBACK_BEGIN(",
    "STEAM_CALLBACK_MEMBER(",
    "STEAM_CALLBACK_ARRAY(",
    "END_CALLBACK_INTERNAL_BEGIN(",
    "END_CALLBACK_INTERNAL_SWITCH(",
    "END_CALLBACK_INTERNAL_END()",
    "STEAM_CALLBACK_END(",
    "INVALID_HTTPCOOKIE_HANDLE",
    "BChatMemberStateChangeRemoved(",
    "STEAM_COLOR_RED(",
    "STEAM_COLOR_GREEN(",
    "STEAM_COLOR_BLUE(",
    "STEAM_COLOR_ALPHA(",
    "INVALID_SCREENSHOT_HANDLE",
    "_snprintf",
    "S_API",
    "STEAM_CALLBACK(",
    "STEAM_CALLBACK_MANUAL(",
    "STEAM_GAMESERVER_CALLBACK(",
    "k_steamIDNil",
    "k_steamIDOutofDateGS",
    "k_steamIDLanModeGS",
    "k_steamIDNotInitYetGS",
    "k_steamIDNonSteamGS",
    "BREAKPAD_INVALID_HANDLE",
    "STEAM_PS3_PATH_MAX",
    "STEAM_PS3_SERVICE_ID_MAX",
    "STEAM_PS3_COMMUNICATION_ID_MAX",
    "STEAM_PS3_COMMUNICATION_SIG_MAX",
    "STEAM_PS3_LANGUAGE_MAX",
    "STEAM_PS3_REGION_CODE_MAX",
    "STEAM_PS3_CURRENT_PARAMS_VER",
    "STEAMPS3_MALLOC_INUSE",
    "STEAMPS3_MALLOC_SYSTEM",
    "STEAMPS3_MALLOC_OK",
    "S_CALLTYPE",
    "POSIX",
    "STEAM_PRIVATE_API(",

    # We just create multiple versions of this struct, Valve renamed them.
    "ControllerAnalogActionData_t",
    "ControllerDigitalActionData_t",
    "ControllerMotionData_t",

    # TODO: Skip all these once we have typedef autogen hooked up.
    #"MASTERSERVERUPDATERPORT_USEGAMESOCKETSHARE",
    #"INVALID_HTTPREQUEST_HANDLE",
)

g_SkippedConstants = (
    # ISteamFriends
    "k_FriendsGroupID_Invalid",

    # ISteamHTMLSurface
    "INVALID_HTMLBROWSER",

    # ISteamInventory
    "k_SteamItemInstanceIDInvalid",
    "k_SteamInventoryResultInvalid",
    "k_SteamInventoryUpdateHandleInvalid",

    # ISteamMatchmaking
    "HSERVERQUERY_INVALID",

    # ISteamRemoteStorage
    "k_UGCHandleInvalid",
    "k_PublishedFileIdInvalid",
    "k_PublishedFileUpdateHandleInvalid",
    "k_UGCFileStreamHandleInvalid",

    # ISteamUGC
    "k_UGCQueryHandleInvalid",
    "k_UGCUpdateHandleInvalid",

    # SteamClientPublic
    "k_HAuthTicketInvalid",

    # SteamTypes
    "k_JobIDNil",
    "k_uBundleIdInvalid",
    "k_uAppIdInvalid",
    "k_uDepotIdInvalid",
    "k_uAPICallInvalid",
    "k_uManifestIdInvalid",
    "k_ulSiteIdInvalid",

    """ TODO: Skip all these once we have typedef autogen hooked up.
    public const ulong k_GIDNil = 0xffffffffffffffffull;
    public const ulong k_TxnIDNil = k_GIDNil;
    public const ulong k_TxnIDUnknown = 0;
    public const int k_uPackageIdFreeSub = 0x0;
    public const int k_uPackageIdInvalid = 0xFFFFFFFF;
    public const ulong k_ulAssetClassIdInvalid = 0x0;
    public const int k_uPhysicalItemIdInvalid = 0x0;
    public const int k_uCellIDInvalid = 0xFFFFFFFF;
    public const int k_uPartnerIdInvalid = 0;"""
)

g_SkippedTypedefs = (
    "uint8",
    "int8",
    "int32",
    "uint32",
    "int64",
    "uint64",
)

g_CustomDefines = {
    # "Name": ("Type", "Value"),
    "MASTERSERVERUPDATERPORT_USEGAMESOCKETSHARE": ("ushort", "0xFFFF"),
    "k_nMaxLobbyKeyLength": ("byte", None),
    "STEAM_CONTROLLER_HANDLE_ALL_CONTROLLERS": ("ulong", "0xFFFFFFFFFFFFFFFF"),
    "STEAM_CONTROLLER_MIN_ANALOG_ACTION_DATA": ("float", "-1.0f"),
    "STEAM_CONTROLLER_MAX_ANALOG_ACTION_DATA": ("float", "1.0f"),
    "STEAM_INPUT_HANDLE_ALL_CONTROLLERS": ("ulong", "0xFFFFFFFFFFFFFFFF"),
    "STEAM_INPUT_MIN_ANALOG_ACTION_DATA": ("float", "-1.0f"),
    "STEAM_INPUT_MAX_ANALOG_ACTION_DATA": ("float", "1.0f"),
}


def main(parser):
    try:
        os.makedirs("autogen/")
    except OSError:
        pass

    lines = []
    defines = parse_defines(parser)
    interfaceversions = defines[0]
    defines = defines[1]
    lines.extend(interfaceversions)
    lines.extend(parse_constants(parser))
    lines.extend(defines)

    with open("autogen/SteamConstants.cs", "wb") as out:
        with open("templates/header.txt", "r") as f:
            out.write(bytes(f.read(), "utf-8"))
        out.write(bytes("namespace Steamworks {\n", "utf-8"))
        out.write(bytes("\tpublic static class Constants {\n", "utf-8"))
        for line in lines:
            out.write(bytes("\t\t" + line + "\n", "utf-8"))
        out.write(bytes("\t}\n", "utf-8"))
        out.write(bytes("}\n\n", "utf-8"))
        out.write(bytes("#endif // !DISABLESTEAMWORKS\n", "utf-8"))


def parse_defines(parser):
    lines = []
    interfaceversions = []
    for f in parser.files:
        for d in f.defines:
            if d.name in g_SkippedDefines:
                continue

            for comment in d.c.precomments:
                lines.append("//" + comment)

            comment = ""
            if d.c.linecomment:
                comment = " //" + d.c.linecomment

            definetype = "int"
            definevalue = d.value
            customdefine = g_CustomDefines.get(d.name, False)
            if customdefine:
                if customdefine[0]:
                    definetype = customdefine[0]
                if customdefine[1]:
                    definevalue = customdefine[1]
            elif d.value.startswith('"'):
                definetype = "string"
                if d.name.startswith("STEAM"):
                    interfaceversions.append("public const " + definetype + " " + d.name + " = " + definevalue + ";" + comment)
                    continue

            lines.append("public const " + definetype + " " + d.name + d.spacing + "= " + definevalue + ";" + comment)

    return (sorted(interfaceversions, key=str.lower), lines)


def parse_constants(parser):
    lines = []
    for f in parser.files:
        for constant in f.constants:
            if constant.name in g_SkippedConstants:
                continue

            for comment in constant.c.precomments:
                lines.append("//" + comment)

            comment = ""
            if constant.c.linecomment:
                comment = " //" + constant.c.linecomment

            constanttype = constant.type
            for t in parser.typedefs:
                if t.name in g_SkippedTypedefs:
                    continue

                if t.name == constant.type:
                    constanttype = t.type
                    break
            constanttype = g_TypeDict.get(constanttype, constanttype)

            constantvalue = constant.value
            if constantvalue == "0xFFFFFFFF":
                constantvalue = "-1"
            elif constantvalue == "0xffffffffffffffffull":
                constantvalue = constantvalue[:-3]

            lines.append("public const " + constanttype + " " + constant.name + " = " + constantvalue + ";" + comment)

    return lines


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("TODO: Usage Instructions")
        exit()

    steamworksparser.Settings.fake_gameserver_interfaces = True
    main(steamworksparser.parse(sys.argv[1]))
