namespace Steamworks
{
	/// Interface used when a custom signal is received.
	/// See ISteamNetworkingSockets::ReceivedP2PCustomSignal
	[System.Serializable]
	[StructLayout(LayoutKind.Sequential)]
	public struct ISteamNetworkingCustomSignalingRecvContext
	{
		/// Called when the signal represents a request for a new connection.
		///
		/// If you want to ignore the request, just return NULL.  In this case,
		/// the peer will NOT receive any reply.  You should consider ignoring
		/// requests rather than actively rejecting them, as a security measure.
		/// If you actively reject requests, then this makes it possible to detect
		/// if a user is online or not, just by sending them a request.
		///
		/// If you wish to send back a rejection, then use
		/// ISteamNetworkingSockets::CloseConnection() and then return NULL.
		/// We will marshal a properly formatted rejection signal and
		/// call SendRejectionSignal() so you can send it to them.
		///
		/// If you return a signaling object, the connection is NOT immediately
		/// accepted by default.  Instead, it stays in the "connecting" state,
		/// and the usual callback is posted, and your app can accept the
		/// connection using ISteamNetworkingSockets::AcceptConnection.  This
		/// may be useful so that these sorts of connections can be more similar
		/// to your application code as other types of connections accepted on
		/// a listen socket.  If this is not useful and you want to skip this
		/// callback process and immediately accept the connection, call
		/// ISteamNetworkingSockets::AcceptConnection before returning the
		/// signaling object.
		///
		/// After accepting a connection (through either means), the connection
		/// will transition into the "finding route" state.
		public IntPtr OnConnectRequest(HSteamNetConnection hConn, ref SteamNetworkingIdentity identityPeer) {
			return NativeMethods.SteamAPI_ISteamNetworkingCustomSignalingRecvContext_OnConnectRequest(ref this, hConn, ref identityPeer);
		}

		/// This is called actively communication rejection or failure
		/// to the incoming message.  If you intend to ignore all incoming requests
		/// that you do not wish to accept, then it's not strictly necessary to
		/// implement this.
		public void SendRejectionSignal(ref SteamNetworkingIdentity identityPeer, IntPtr pMsg, int cbMsg) {
			NativeMethods.SteamAPI_ISteamNetworkingCustomSignalingRecvContext_SendRejectionSignal(ref this, ref identityPeer, pMsg, cbMsg);
		}
	}
}

#endif // !DISABLESTEAMWORKS