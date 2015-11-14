using System;
using System.Net;
using System.Web;

namespace Electro.Utils
{
	internal static class CookieHelper
	{
		public static void SetCookie(this HttpListenerResponse response, string name, string value, bool httpOnly = false)
		{
			var expires = DateTime.UtcNow.AddDays(30);
			//NOTE: M$.NET multiple cookies merged under one Set-Cookie header in the HTTP response when using "HttpListenerResponse.SetCookie" method
			response.Headers.Add(HttpResponseHeader.SetCookie, string.Format("{0}={1}; expires={2}; path=/{3}", HttpUtility.UrlEncode(name), value == null ? null : HttpUtility.UrlEncode(value), expires.ToString("R"), httpOnly ? "; HttpOnly" : null));
			//response.Cookies.Add(new Cookie(HttpUtility.UrlEncode(name), value == null ? string.Empty : HttpUtility.UrlEncode(value)) {Expires = expires, HttpOnly = httpOnly});
		}
	}
}