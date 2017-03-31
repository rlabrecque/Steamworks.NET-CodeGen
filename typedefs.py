import os
import sys
import errno
import shutil
from collections import OrderedDict
from SteamworksParser import steamworksparser

g_PrettyFilenames = {
    "SteamClientpublic": "SteamClientPublic",
    "SteamHtmlsurface": "SteamHTMLSurface",
    "SteamHttp": "SteamHTTP",
    "SteamRemotestorage": "SteamRemoteStorage",
    "SteamUgc": "SteamUGC",
    "SteamUnifiedmessages": "SteamUnifiedMessages",
    "SteamUserstats": "SteamUserStats",
}

g_TypeDict = {
    "int16": "short",
    "int32": "int",
    "uint32": "uint",
    "uint64": "ulong",
    "void*": "System.IntPtr"
}

g_UnusedTypedefs = [
    # SteamClientPublic
    "BREAKPAD_HANDLE",

    # SteamTypes
    "AssetClassId_t",
    "BundleId_t",
    "CellID_t",
    "GID_t",
    "int8",
    "int16",
    "int32",
    "int64",
    "intp",
    "JobID_t",
    "lint64",
    "PackageId_t",
    "PartnerId_t",
    "PhysicalItemId_t",
    "RTime32",
    "TxnID_t",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "uintp",
    "ulint64",
]

g_ReadOnlyValues = {
    "HAuthTicket": OrderedDict([
        ("Invalid", "0"),
    ]),

    "FriendsGroupID_t": OrderedDict([
        ("Invalid", "-1"),
    ]),

    "HHTMLBrowser": OrderedDict([
        ("Invalid", "0"),
    ]),

    "HTTPCookieContainerHandle": OrderedDict([
        ("Invalid", "0"),
    ]),

    "HTTPRequestHandle": OrderedDict([
        ("Invalid", "0"),
    ]),

    "SteamInventoryResult_t": OrderedDict([
        ("Invalid", "-1"),
    ]),

    "SteamItemInstanceID_t": OrderedDict([
        ("Invalid", "0xFFFFFFFFFFFFFFFF"),
    ]),

    "HServerListRequest": OrderedDict([
        ("Invalid", "System.IntPtr.Zero"),
    ]),

    "HServerQuery": OrderedDict([
        ("Invalid", "-1"),
    ]),

    "PublishedFileId_t": OrderedDict([
        ("Invalid", "0"),
    ]),

    "PublishedFileUpdateHandle_t": OrderedDict([
        ("Invalid", "0xffffffffffffffff"),
    ]),

    "UGCFileWriteStreamHandle_t": OrderedDict([
        ("Invalid", "0xffffffffffffffff"),
    ]),

    "UGCHandle_t": OrderedDict([
        ("Invalid", "0xffffffffffffffff"),
    ]),

    "ScreenshotHandle": OrderedDict([
        ("Invalid", "0"),
    ]),

    "AppId_t": OrderedDict([
        ("Invalid", "0x0"),
    ]),

    "DepotId_t": OrderedDict([
        ("Invalid", "0x0"),
    ]),

    "ManifestId_t": OrderedDict([
        ("Invalid", "0x0"),
    ]),

    "SteamAPICall_t": OrderedDict([
        ("Invalid", "0x0"),
    ]),

    "UGCQueryHandle_t": OrderedDict([
        ("Invalid", "0xffffffffffffffff"),
    ]),

    "UGCUpdateHandle_t": OrderedDict([
        ("Invalid", "0xffffffffffffffff"),
    ]),

    "ClientUnifiedMessageHandle": OrderedDict([
        ("Invalid", "0"),
    ]),
}


def main(parser):
    try:
        shutil.rmtree("types/")
    except FileNotFoundError:
        pass

    try:
        shutil.copytree("CustomTypes/", "types/")
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy("CustomTypes/", "types/")
        else:
            print('Directory not copied. Error: %s' % e)

    with open("templates/typetemplate.txt", "r") as f:
        template = f.read()

    for t in parser.typedefs:
        if t.name in g_UnusedTypedefs:
            continue

        readonly = ""
        try:
            for k, v in g_ReadOnlyValues[t.name].items():
                readonly += "\t\tpublic static readonly " + t.name + " " + k + " = new " + t.name + "(" + v + ");\n"
        except KeyError:
            pass

        ourtemplate = template
        ourtype = g_TypeDict.get(t.type, t.type)
        if ourtype == "System.IntPtr":
            ourtemplate = ourtemplate.replace(", System.IComparable<{NAME}>", "", 1)
            ourtemplate = ourtemplate.replace("""
\t\tpublic int CompareTo({NAME} other) {
\t\t\treturn m_{NAMESTRIPPED}.CompareTo(other.m_{NAMESTRIPPED});
\t\t}
""", "", 1)

        ourtemplate = ourtemplate.replace("{NAME}", t.name)
        ourtemplate = ourtemplate.replace("{NAMESTRIPPED}", t.name.replace("_t", "", 1))
        ourtemplate = ourtemplate.replace("{TYPE}", ourtype)
        ourtemplate = ourtemplate.replace("{READONLY}\n", readonly)

        foldername = os.path.splitext(t.filename)[0]
        foldername = foldername.replace("isteam", "steam", 1)
        foldername = "Steam" + foldername[len("Steam"):].capitalize()
        foldername = g_PrettyFilenames.get(foldername, foldername)

        try:
            os.makedirs("types/" + foldername)
        except OSError:
            pass

        with open("types/" + foldername + "/" + t.name + ".cs", "wb") as out:
            out.write(bytes(ourtemplate, "utf-8"))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("TODO: Usage Instructions")
        exit()

    steamworksparser.Settings.fake_gameserver_interfaces = True
    main(steamworksparser.parse(sys.argv[1]))
