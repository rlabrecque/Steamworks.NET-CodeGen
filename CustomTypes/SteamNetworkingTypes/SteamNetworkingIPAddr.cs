namespace Steamworks
{
	/// Store an IP and port.  IPv6 is always used; IPv4 is represented using
	/// "IPv4-mapped" addresses: IPv4 aa.bb.cc.dd => IPv6 ::ffff:aabb:ccdd
	/// (RFC 4291 section 2.5.5.2.)
	[System.Serializable]
	[StructLayout(LayoutKind.Sequential, Pack = 1)]
	public struct SteamNetworkingIPAddr : System.IEquatable<SteamNetworkingIPAddr>
	{
		[MarshalAs(UnmanagedType.ByValArray, SizeConst = 16)]
		public byte[] m_ipv6;
		public ushort m_port; // Host byte order

		// Max length of the buffer needed to hold IP formatted using ToString, including '\0'
		// ([0123:4567:89ab:cdef:0123:4567:89ab:cdef]:12345)
		public const int k_cchMaxString = 48;

		 // Set everything to zero.  E.g. [::]:0
		public void Clear() {
			NativeMethods.SteamAPI_SteamNetworkingIPAddr_Clear(ref this);
		}

		// Return true if the IP is ::0.  (Doesn't check port.)
		public bool IsIPv6AllZeros() {
			return NativeMethods.SteamAPI_SteamNetworkingIPAddr_IsIPv6AllZeros(ref this);
		}

		// Set IPv6 address.  IP is interpreted as bytes, so there are no endian issues.  (Same as inaddr_in6.)  The IP can be a mapped IPv4 address
		public void SetIPv6(byte[] ipv6, ushort nPort) {
			NativeMethods.SteamAPI_SteamNetworkingIPAddr_SetIPv6(ref this, ipv6, nPort);
		}

		// Sets to IPv4 mapped address.  IP and port are in host byte order.
		public void SetIPv4(uint nIP, ushort nPort) {
			NativeMethods.SteamAPI_SteamNetworkingIPAddr_SetIPv4(ref this, nIP, nPort);
		}

		// Return true if IP is mapped IPv4
		public bool IsIPv4() {
			return NativeMethods.SteamAPI_SteamNetworkingIPAddr_IsIPv4(ref this);
		}

		// Returns IP in host byte order (e.g. aa.bb.cc.dd as 0xaabbccdd).  Returns 0 if IP is not mapped IPv4.
		public uint GetIPv4() {
			return NativeMethods.SteamAPI_SteamNetworkingIPAddr_GetIPv4(ref this);
		}

		// Set to the IPv6 localhost address ::1, and the specified port.
		public void SetIPv6LocalHost(ushort nPort = 0) {
			NativeMethods.SteamAPI_SteamNetworkingIPAddr_SetIPv6LocalHost(ref this, nPort);
		}

		// Return true if this identity is localhost.  (Either IPv6 ::1, or IPv4 127.0.0.1)
		public bool IsLocalHost() {
			return NativeMethods.SteamAPI_SteamNetworkingIPAddr_IsLocalHost(ref this);
		}

		/// Print to a string, with or without the port.  Mapped IPv4 addresses are printed
		/// as dotted decimal (12.34.56.78), otherwise this will print the canonical
		/// form according to RFC5952.  If you include the port, IPv6 will be surrounded by
		/// brackets, e.g. [::1:2]:80.  Your buffer should be at least k_cchMaxString bytes
		/// to avoid truncation
		///
		/// See also SteamNetworkingIdentityRender
		public void ToString(out string buf, bool bWithPort) {
			IntPtr buf2 = Marshal.AllocHGlobal(k_cchMaxString);
			NativeMethods.SteamNetworkingIPAddr_ToString(ref this, buf2, k_cchMaxString, bWithPort);
			buf = InteropHelp.PtrToStringUTF8(buf2);
			Marshal.FreeHGlobal(buf2);
		}

		/// Parse an IP address and optional port.  If a port is not present, it is set to 0.
		/// (This means that you cannot tell if a zero port was explicitly specified.)
		public bool ParseString(string pszStr) {
			using (var pszStr2 = new InteropHelp.UTF8StringHandle(pszStr)) {
				return NativeMethods.SteamNetworkingIPAddr_ParseString(ref this, pszStr2);
			}
		}

		/// See if two addresses are identical
		public bool Equals(SteamNetworkingIPAddr x) {
			return NativeMethods.SteamAPI_SteamNetworkingIPAddr_IsEqualTo(ref this, ref x);
		}
	}
}

#endif // !DISABLESTEAMWORKS
