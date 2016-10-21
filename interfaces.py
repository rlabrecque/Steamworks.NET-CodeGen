import os
import sys
from SteamworksParser import steamworksparser

g_SkippedFiles = (
    # We don't currently support the following interfaces because they don't provide a factory of their own.
    # You are expected to call GetISteamGeneric to get them.
    "isteamappticket.h",
    "isteamgamecoordinator.h",
    # PS3 is not supported.
    "isteamps3overlayrenderer.h",
)

g_TypeDict = {
    # Built in types
    "char *": "IntPtr",
    "char **": "out IntPtr",
    "const char*": "InteropHelp.UTF8StringHandle",
    "const char *": "InteropHelp.UTF8StringHandle",

    "const void *": "IntPtr",
    "unsigned short": "ushort",
    "void *": "IntPtr",
    "void*": "IntPtr",

    "uint8": "byte",

    "int16": "short",
    "uint16": "ushort",

    "int32": "int",
    "uint32": "uint",
    "unsigned int": "uint",
    "const uint32": "uint",

    "int64": "long",
    "uint64": "ulong",
    "uint64_t": "ulong",

    # Only used in FileLoadDialogResponse
    "const char **": "IntPtr",

    "RTime32": "uint",
    "const SteamItemInstanceID_t": "SteamItemInstanceID_t",
    "const SteamItemDef_t": "SteamItemDef_t",
    "SteamParamStringArray_t *": "IntPtr",
    "const SteamParamStringArray_t *": "IntPtr",
    "ISteamMatchmakingServerListResponse *": "IntPtr",
    "ISteamMatchmakingPingResponse *": "IntPtr",
    "ISteamMatchmakingPlayersResponse *": "IntPtr",
    "ISteamMatchmakingRulesResponse *": "IntPtr",
    #"MatchMakingKeyValuePair_t **": "IntPtr", HACK in parse_args()
}

g_WrapperArgsTypeDict = {
    "SteamParamStringArray_t *": "System.Collections.Generic.IList<string>",
    "const SteamParamStringArray_t *": "System.Collections.Generic.IList<string>",
    "ISteamMatchmakingServerListResponse *": "ISteamMatchmakingServerListResponse",
    "ISteamMatchmakingPingResponse *": "ISteamMatchmakingPingResponse",
    "ISteamMatchmakingPlayersResponse *": "ISteamMatchmakingPlayersResponse",
    "ISteamMatchmakingRulesResponse *": "ISteamMatchmakingRulesResponse",
    "MatchMakingKeyValuePair_t **": "MatchMakingKeyValuePair_t[]",
    "char **": "out string",
}

g_ReturnTypeDict = {
    # Built in types
    "const char *": "IntPtr",

    # Steamworks types
    "CSteamID": "ulong",
    "gameserveritem_t *": "IntPtr",

    # TODO: UGH
    "ISteamAppList *": "IntPtr",
    "ISteamApps *": "IntPtr",
    "ISteamController *": "IntPtr",
    "ISteamFriends *": "IntPtr",
    "ISteamGameServer *": "IntPtr",
    "ISteamGameServerStats *": "IntPtr",
    "ISteamHTMLSurface *": "IntPtr",
    "ISteamHTTP *": "IntPtr",
    "ISteamInventory *": "IntPtr",
    "ISteamInventory *": "IntPtr",
    "ISteamMatchmaking *": "IntPtr",
    "ISteamMatchmakingServers *": "IntPtr",
    "ISteamMusic *": "IntPtr",
    "ISteamMusicRemote *": "IntPtr",
    "ISteamNetworking *": "IntPtr",
    "ISteamPS3OverlayRender *": "IntPtr",
    "ISteamRemoteStorage *": "IntPtr",
    "ISteamScreenshots *": "IntPtr",
    "ISteamUGC *": "IntPtr",
    "ISteamUnifiedMessages *": "IntPtr",
    "ISteamUser *": "IntPtr",
    "ISteamUserStats *": "IntPtr",
    "ISteamUtils *": "IntPtr",
    "ISteamVideo *": "IntPtr",
}

g_SpecialReturnTypeDict = {
    "ISteamUtils_GetAppID": "AppId_t",
    "ISteamGameServerUtils_GetAppID": "AppId_t",
}

g_SpecialArgsDict = {
    # These args are missing a clang attribute like ARRAY_COUNT
    "ISteamAppList_GetInstalledApps": {
        "pvecAppID": "AppId_t[]",
    },
    "ISteamApps_GetInstalledDepots": {
        "pvecDepots": "DepotId_t[]",
    },
    "ISteamController_GetConnectedControllers": {
        "handlesOut": "ControllerHandle_t[]",
    },
    "ISteamController_GetDigitalActionOrigins": {
        "originsOut": "EControllerActionOrigin[]",
    },
    "ISteamController_GetAnalogActionOrigins": {
        "originsOut": "EControllerActionOrigin[]",
    },
    "ISteamGameServer_SendUserConnectAndAuthenticate": {
        "pvAuthBlob": "byte[]",
    },
    "ISteamGameServer_GetAuthSessionTicket": {
        "pTicket": "byte[]",
    },
    "ISteamGameServer_BeginAuthSession": {
        "pAuthTicket": "byte[]",
    },
    "ISteamGameServer_HandleIncomingPacket": {
        "pData": "byte[]",
    },
    "ISteamGameServer_GetNextOutgoingPacket": {
        "pOut": "byte[]",
    },
    "ISteamHTTP_GetHTTPResponseHeaderValue": {
        "pHeaderValueBuffer": "byte[]",
    },
    "ISteamHTTP_GetHTTPResponseBodyData": {
        "pBodyDataBuffer": "byte[]",
    },
    "ISteamHTTP_GetHTTPStreamingResponseBodyData": {
        "pBodyDataBuffer": "byte[]",
    },
    "ISteamHTTP_SetHTTPRequestRawPostBody": {
        "pubBody": "byte[]",
    },
    "ISteamInventory_SerializeResult": {
        "pOutBuffer": "byte[]",
    },
    "ISteamInventory_DeserializeResult": {
        "pBuffer": "byte[]",
    },
    "ISteamMatchmaking_SendLobbyChatMsg": {
        "pvMsgBody": "byte[]",
    },
    "ISteamMatchmaking_GetLobbyChatEntry": {
        "pvData": "byte[]",
    },
    "ISteamMusicRemote_SetPNGIcon_64x64": {
        "pvBuffer": "byte[]",
    },
    "ISteamMusicRemote_UpdateCurrentEntryCoverArt": {
        "pvBuffer": "byte[]",
    },
    "ISteamNetworking_SendP2PPacket": {
        "pubData": "byte[]",
    },
    "ISteamNetworking_ReadP2PPacket": {
        "pubDest": "byte[]",
    },
    "ISteamNetworking_SendDataOnSocket": {
        "pubData": "byte[]",
    },
    "ISteamNetworking_RetrieveDataFromSocket": {
        "pubDest": "byte[]",
    },
    "ISteamNetworking_RetrieveData": {
        "pubDest": "byte[]",
    },
    "ISteamRemoteStorage_FileWrite": {
        "pvData": "byte[]",
    },
    "ISteamRemoteStorage_FileRead": {
        "pvData": "byte[]",
    },
    "ISteamRemoteStorage_FileWriteAsync": {
        "pvData": "byte[]",
    },
    "ISteamRemoteStorage_FileReadAsyncComplete": {
        "pvBuffer": "byte[]",
    },
    "ISteamRemoteStorage_FileWriteStreamWriteChunk": {
        "pvData": "byte[]",
    },
    "ISteamRemoteStorage_UGCRead": {
        "pvData": "byte[]",
    },
    "ISteamScreenshots_WriteScreenshot": {
        "pubRGB": "byte[]",
    },
    "ISteamUGC_CreateQueryUGCDetailsRequest": {
        "pvecPublishedFileID": "PublishedFileId_t[]",
    },
    "ISteamUGC_GetQueryUGCChildren": {
        "pvecPublishedFileID": "PublishedFileId_t[]",
    },
    "ISteamUGC_GetSubscribedItems": {
        "pvecPublishedFileID": "PublishedFileId_t[]",
    },
    "ISteamUGC_StartPlaytimeTracking": {
        "pvecPublishedFileID": "PublishedFileId_t[]",
    },
    "ISteamUGC_StopPlaytimeTracking": {
        "pvecPublishedFileID": "PublishedFileId_t[]",
    },
    "ISteamUnifiedMessages_SendMethod": {
        "pRequestBuffer": "byte[]",
    },
    "ISteamUnifiedMessages_GetMethodResponseData": {
        "pResponseBuffer": "byte[]",
    },
    "ISteamUnifiedMessages_SendNotification": {
        "pNotificationBuffer": "byte[]",
    },
    "ISteamUser_InitiateGameConnection": {
        "pAuthBlob": "byte[]",
    },
    "ISteamUser_GetVoice": {
        "pDestBuffer": "byte[]",
        "pUncompressedDestBuffer": "byte[]",
    },
    "ISteamUser_DecompressVoice": {
        "pCompressed": "byte[]",
        "pDestBuffer": "byte[]",
    },
    "ISteamUser_GetAuthSessionTicket": {
        "pTicket": "byte[]",
    },
    "ISteamUser_BeginAuthSession": {
        "pAuthTicket": "byte[]",
    },
    "ISteamUser_RequestEncryptedAppTicket": {
        "pDataToInclude": "byte[]",
    },
    "ISteamUser_GetEncryptedAppTicket": {
        "pTicket": "byte[]",
    },
    "ISteamUserStats_GetDownloadedLeaderboardEntry": {
        "pDetails": "int[]",
    },
    "ISteamUserStats_UploadLeaderboardScore": {
        "pScoreDetails": "int[]",
    },
    "ISteamUtils_GetImageRGBA": {
        "pubDest": "byte[]",
    },

    # GameServer Copies
    "ISteamGameServerHTTP_GetHTTPResponseHeaderValue": {
        "pHeaderValueBuffer": "byte[]",
    },
    "ISteamGameServerHTTP_GetHTTPResponseBodyData": {
        "pBodyDataBuffer": "byte[]",
    },
    "ISteamGameServerHTTP_GetHTTPStreamingResponseBodyData": {
        "pBodyDataBuffer": "byte[]",
    },
    "ISteamGameServerHTTP_SetHTTPRequestRawPostBody": {
        "pubBody": "byte[]",
    },
    "ISteamGameServerInventory_SerializeResult": {
        "pOutBuffer": "byte[]",
    },
    "ISteamGameServerInventory_DeserializeResult": {
        "pBuffer": "byte[]",
    },
    "ISteamGameServerNetworking_SendP2PPacket": {
        "pubData": "byte[]",
    },
    "ISteamGameServerNetworking_ReadP2PPacket": {
        "pubDest": "byte[]",
    },
    "ISteamGameServerNetworking_SendDataOnSocket": {
        "pubData": "byte[]",
    },
    "ISteamGameServerNetworking_RetrieveDataFromSocket": {
        "pubDest": "byte[]",
    },
    "ISteamGameServerNetworking_RetrieveData": {
        "pubDest": "byte[]",
    },
    "ISteamGameServerUtils_GetImageRGBA": {
        "pubDest": "byte[]",
    },
    "ISteamGameServerUGC_CreateQueryUGCDetailsRequest": {
        "pvecPublishedFileID": "PublishedFileId_t[]",
    },
    "ISteamGameServerUGC_GetQueryUGCChildren": {
        "pvecPublishedFileID": "PublishedFileId_t[]",
    },
    "ISteamGameServerUGC_GetSubscribedItems": {
        "pvecPublishedFileID": "PublishedFileId_t[]",
    },
    "ISteamGameServerUGC_StartPlaytimeTracking": {
        "pvecPublishedFileID": "PublishedFileId_t[]",
    },
    "ISteamGameServerUGC_StopPlaytimeTracking": {
        "pvecPublishedFileID": "PublishedFileId_t[]",
    },

    # This is a little nicety that we provide, I don't know why Valve doesn't just change it.
    "ISteamFriends_GetFriendCount": {
        "iFriendFlags": "EFriendFlags",
    },
    "ISteamFriends_GetFriendByIndex": {
        "iFriendFlags": "EFriendFlags",
    },
    "ISteamFriends_HasFriend": {
        "iFriendFlags": "EFriendFlags",
    },

    # These end up being "out type", when we need them to be "ref type"
    "ISteamInventory_GetResultItems": {
        "punOutItemsArraySize": "ref uint",
    },
    "ISteamInventory_GetItemDefinitionProperty": {
        "punValueBufferSizeOut": "ref uint",
    },
    "ISteamGameServerInventory_GetResultItems": {
        "punOutItemsArraySize": "ref uint",
    },
    "ISteamGameServerInventory_GetItemDefinitionProperty": {
        "punValueBufferSizeOut": "ref uint",
    },
}

g_SpecialWrapperArgsDict = {
    # These are void* but we want out string
    "ISteamFriends_GetClanChatMessage": {
        "prgchText": "out string",
    },
    "ISteamFriends_GetFriendMessage": {
        "pvData": "out string",
    },
}

g_SpecialOutStringRetCmp = {
    "ISteamFriends_GetClanChatMessage": "ret != 0",
    "ISteamFriends_GetFriendMessage": "ret != 0",
}

g_SkippedTypedefs = (
    "uint8",
    "int8",
    "int32",
    "uint32",
    "int64",
    "uint64",
)

HEADER = None

g_NativeMethods = []
g_Output = []
g_funcNames = []
g_Typedefs = None

def main(parser):
    try:
        os.makedirs("autogen/")
    except OSError:
        pass

    with open("header.txt", "r") as f:
        global HEADER
        HEADER = f.read()

    global g_Typedefs
    g_Typedefs = parser.typedefs
    for f in parser.files:
        parse(f)

    with open("autogen/NativeMethods.cs", "wb") as out:
        out.write(bytes(HEADER, "utf-8"))
        out.write(bytes("\tinternal static class NativeMethods {\n", "utf-8"))
        out.write(bytes("\t\tinternal const string NativeLibraryName = \"CSteamworks\";\n", "utf-8"))
        with open("steam_api.txt", "r") as f:
            out.write(bytes(f.read(), "utf-8"))
        for line in g_NativeMethods:
            out.write(bytes(line + "\n", "utf-8"))
        out.write(bytes("\t}\n", "utf-8"))
        out.write(bytes("}\n\n", "utf-8"))
        out.write(bytes("#endif // !DISABLESTEAMWORKS\n", "utf-8"))


def parse(f):
    if f.name in g_SkippedFiles:
        return

    print("File: " + f.name)

    del g_Output[:]
    for interface in f.interfaces:
        print(" - " + interface.name)
        g_Output.append('\tpublic static class ' + interface.name[1:] + ' {')
        parse_interface(f, interface)

    if g_Output:
        with open('autogen/' + os.path.splitext(f.name)[0] + '.cs', 'wb') as out:
            out.write(bytes(HEADER, "utf-8"))
            for line in g_Output:
                out.write(bytes(line + "\n", "utf-8"))
            out.write(bytes("}\n\n", "utf-8"))  # Namespace
            out.write(bytes("#endif // !DISABLESTEAMWORKS\n", "utf-8"))


def parse_interface(f, interface):
    del g_funcNames[:]

    g_NativeMethods.append("#region " + interface.name[1:])
    lastIfStatement = None
    for func in interface.functions:
        if func.ifstatements != lastIfStatement:
            if lastIfStatement is not None:
                g_NativeMethods[-1] = "#endif"
                g_Output[-1] = "#endif"
                lastIfStatement = None
                if func.ifstatements:
                    g_NativeMethods.append("#if " + func.ifstatements.replace("defined(", "").replace(")", ""))
                    g_Output.append("#if " + func.ifstatements.replace("defined(", "").replace(")", ""))
                    lastIfStatement = func.ifstatements
            elif func.ifstatements:
                g_NativeMethods[-1] = "#if " + func.ifstatements.replace("defined(", "").replace(")", "")
                g_NativeMethods[-1] = "#if " + func.ifstatements.replace("defined(", "").replace(")", "")
                g_Output[-1] = "#if " + func.ifstatements.replace("defined(", "").replace(")", "")
                lastIfStatement = func.ifstatements

        if func.private:
            continue

        parse_func(f, interface, func)

    # Remove last whitespace
    del g_NativeMethods[-1]
    del g_Output[-1]

    if lastIfStatement is not None:
        g_NativeMethods.append("#endif")
        g_Output.append("#endif")

    g_NativeMethods.append("#endregion")
    g_Output.append("\t}")

def parse_func(f, interface, func):
    if func.name in g_funcNames:
        func.name += "_"
    g_funcNames.append(func.name)

    strEntryPoint = interface.name + "_" + func.name

    wrapperreturntype = None
    strCast = ""
    returntype = func.returntype
    returntype = g_SpecialReturnTypeDict.get(strEntryPoint, returntype)
    for t in g_Typedefs:
        if t.name == returntype:
            if t.name not in g_SkippedTypedefs:
                wrapperreturntype = returntype
                strCast = "(" + returntype + ")"
                returntype = t.type
            break
    returntype = g_TypeDict.get(returntype, returntype)
    returntype = g_TypeDict.get(func.returntype, returntype)
    returntype = g_ReturnTypeDict.get(func.returntype, returntype)
    if wrapperreturntype == None:
        wrapperreturntype = returntype

    args = parse_args(strEntryPoint, func.args)
    pinvokeargs = args[0]  # TODO: NamedTuple
    wrapperargs = args[1]
    argnames = args[2]
    stringargs = args[3]
    outstringargs = args[4][0]
    outstringsize = args[4][1]

    g_NativeMethods.append("\t\t[DllImport(NativeLibraryName, CallingConvention = CallingConvention.Cdecl)]")

    if returntype == "bool":
        g_NativeMethods.append("\t\t[return: MarshalAs(UnmanagedType.I1)]")

    g_NativeMethods.append("\t\tpublic static extern " + returntype + " " + strEntryPoint + "(" + pinvokeargs + ");")
    g_NativeMethods.append("")

    functionBody = []

    if 'GameServer' in interface.name:
        functionBody.append("\t\t\tInteropHelp.TestIfAvailableGameServer();")
    else:
        functionBody.append("\t\t\tInteropHelp.TestIfAvailableClient();")

    strReturnable = "return "
    if func.returntype == "void":
        strReturnable = ""
    elif func.returntype == "const char *":
        wrapperreturntype = "string"
        strReturnable += "InteropHelp.PtrToStringUTF8("
        argnames += ")"
    elif func.returntype == "gameserveritem_t *":
        wrapperreturntype = "gameserveritem_t"
        strReturnable += "(gameserveritem_t)Marshal.PtrToStructure("
        argnames += "), typeof(gameserveritem_t)"
    elif func.returntype == "CSteamID":
        wrapperreturntype = "CSteamID"
        strReturnable += "(CSteamID)"

    if outstringargs:
        strReturnable = returntype + " ret = "
        for i, a in enumerate(outstringargs):
            if not outstringsize:
                functionBody.append("\t\t\tIntPtr " + a + "2;")
                continue
            cast = ""
            if outstringsize[i].type != "int":
                cast = "(int)"

            functionBody.append("\t\t\tIntPtr " + a + "2 = Marshal.AllocHGlobal(" + cast + outstringsize[i].name + ");")

    indentlevel = "\t\t\t"
    if stringargs:
        indentlevel += "\t"
        for a in stringargs:
            functionBody.append("\t\t\tusing (var " + a + "2 = new InteropHelp.UTF8StringHandle(" + a + "))")

        functionBody[-1] += " {"

    functionBody.append("{0}{1}{2}NativeMethods.{3}({4});".format(indentlevel, strReturnable, strCast, strEntryPoint, argnames))

    if outstringargs:
        retcmp = "ret != 0"
        if returntype == "bool":
            retcmp = "ret"
        elif returntype == "int":
            retcmp = "ret != -1"
        retcmp = g_SpecialOutStringRetCmp.get(strEntryPoint, retcmp)
        for a in outstringargs:
            functionBody.append(indentlevel + a + " = " + retcmp + " ? InteropHelp.PtrToStringUTF8(" + a + "2) : null;")
            if strEntryPoint != "ISteamRemoteStorage_GetUGCDetails":
                functionBody.append(indentlevel + "Marshal.FreeHGlobal(" + a + "2);")
        functionBody.append(indentlevel + "return ret;")

    if stringargs:
        functionBody.append("\t\t\t}")

    comments = func.comments
    if func.linecomment:
        comments.append(func.linecomment)

    if comments:
        g_Output.append("\t\t/// <summary>")
        for c in comments:
            c = c.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')#.replace('/*', '').replace('*/', '')
            if c:
                g_Output.append("\t\t/// <para>" + c + "</para>")
        g_Output.append("\t\t/// </summary>")
    g_Output.append("\t\tpublic static " + wrapperreturntype + " " + func.name.rstrip("_") + "(" + wrapperargs + ") {")

    g_Output.extend(functionBody)

    g_Output.append("\t\t}")
    g_Output.append("")

def parse_args(strEntryPoint, args):
    pinvokeargs = ""
    wrapperargs = ""
    argnames = ""
    stringargs = []
    outstringargs = []
    outstringsize = []

    getsize = False
    for arg in args:
        argtype = g_TypeDict.get(arg.type, arg.type)
        if argtype.endswith("*"):
            potentialtype = arg.type.rstrip("*").rstrip()
            argtype = "out " + g_TypeDict.get(potentialtype, potentialtype)
        argtype = g_SpecialArgsDict.get(strEntryPoint, dict()).get(arg.name, argtype)

        if arg.attribute:
            if arg.attribute.name == "OUT_ARRAY" or arg.attribute.name == "OUT_ARRAY_CALL" or arg.attribute.name == "OUT_ARRAY_COUNT" or arg.attribute.name == "ARRAY_COUNT" or arg.attribute.name == "ARRAY_COUNT_D":
                potentialtype = arg.type.rstrip("*").rstrip()
                argtype = g_TypeDict.get(potentialtype, potentialtype) + "[]"
            #if arg.attribute.name == "OUT_STRING" or arg.attribute.name == "OUT_STRING_COUNT":  #Unused for now

        if arg.type == "MatchMakingKeyValuePair_t **":  # TODO: Fixme - Small Hack... We do this because MatchMakingKeyValuePair's have ARRAY_COUNT() and two **'s, things get broken :(
            argtype = "IntPtr"

        if argtype.endswith("[]"):
            argtype = "[In, Out] " + argtype
        elif argtype == "bool":
            argtype = "[MarshalAs(UnmanagedType.I1)] " + argtype

        pinvokeargs += argtype + " " + arg.name + ", "

        argtype = argtype.replace("[In, Out] ", "").replace("[MarshalAs(UnmanagedType.I1)] ", "")
        wrapperargtype = g_WrapperArgsTypeDict.get(arg.type, argtype)
        wrapperargtype = g_SpecialWrapperArgsDict.get(strEntryPoint, dict()).get(arg.name, wrapperargtype)
        if wrapperargtype == "InteropHelp.UTF8StringHandle":
            wrapperargtype = "string"
        elif arg.type == "char *":
            wrapperargtype = "out string"
        wrapperargs += wrapperargtype + " " + arg.name
        if arg.default:
            wrapperargs += " = " + arg.default
        wrapperargs += ", "

        if argtype.startswith("out"):
            argnames += "out "
        elif argtype.startswith("ref"):
            argnames += "ref "

        if wrapperargtype == "System.Collections.Generic.IList<string>":
            argnames += "new InteropHelp.SteamParamStringArray(" + arg.name + ")"
        elif wrapperargtype == "MatchMakingKeyValuePair_t[]":
            argnames += "new MMKVPMarshaller(" + arg.name + ")"
        elif wrapperargtype.endswith("Response"):
            argnames += "(IntPtr)" + arg.name
        else:
            argnames += arg.name

        if getsize:
            getsize = False
            outstringsize.append(arg)

        if wrapperargtype == "string":
            stringargs.append(arg.name)
            argnames += "2"
        elif wrapperargtype == "out string":
            outstringargs.append(arg.name)
            argnames += "2"
            if strEntryPoint != "ISteamRemoteStorage_GetUGCDetails":
                getsize = True

        argnames += ", "
    pinvokeargs = pinvokeargs.rstrip(", ")
    wrapperargs = wrapperargs.rstrip(", ")
    argnames = argnames.rstrip(", ")
    return (pinvokeargs, wrapperargs, argnames, stringargs, (outstringargs, outstringsize))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("TODO: Usage Instructions")
        exit()

    steamworksparser.Settings.fake_gameserver_interfaces = True
    main(steamworksparser.parse(sys.argv[1]))
