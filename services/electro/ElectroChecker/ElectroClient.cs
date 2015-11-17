using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Numerics;
using System.Text;
using System.Threading.Tasks;
using System.Web;
using Electro.Crypto;
using Electro.Handlers;
using Electro.Model;
using Electro.Utils;

namespace ElectroChecker
{
	class ElectroClient
	{
		public static CookieCollection RegUser(string host, int port, string login, string pass, string publicMessage = null, string privateNotes = null)
		{
			var request = CreateRequest(string.Format("http://{0}:{1}/register", host, port), WebRequestMethods.Http.Post);

			var data = Encoding.UTF8.GetBytes(string.Format("login={0}&pass={1}&publicMessage={2}&privateNotes={3}", HttpUtility.UrlEncode(login), HttpUtility.UrlEncode(pass), HttpUtility.UrlEncode(publicMessage), HttpUtility.UrlEncode(privateNotes) ));
			using(var requestStream = request.GetRequestStream())
				requestStream.Write(data, 0, data.Length);

			using(var response = (HttpWebResponse)request.GetResponse())
			{
				return response.Cookies;
			}
		}

		public static CookieCollection LoginUser(string host, int port, string login, string pass)
		{
			var request = CreateRequest(string.Format("http://{0}:{1}/login", host, port), WebRequestMethods.Http.Post);

			var data = Encoding.UTF8.GetBytes(string.Format("login={0}&pass={1}", HttpUtility.UrlEncode(login), HttpUtility.UrlEncode(pass)));
			using(var requestStream = request.GetRequestStream())
				requestStream.Write(data, 0, data.Length);

			using(var response = (HttpWebResponse)request.GetResponse())
			{
				return response.Cookies;
			}
		}

		public static Election StartElection(string host, int port, CookieCollection cookieCollection, string name, bool isPublic, int nominateDuration, int voteDuration)
		{
			var request = CreateRequest(string.Format("http://{0}:{1}/startElection", host, port), WebRequestMethods.Http.Post, cookieCollection);

			var data = Encoding.UTF8.GetBytes(string.Format("name={0}&isPublic={1}&nominateDuration={2}&voteDuration={3}", HttpUtility.UrlEncode(name), isPublic, nominateDuration, voteDuration));
			using(var requestStream = request.GetRequestStream())
				requestStream.Write(data, 0, data.Length);

			using(var response = (HttpWebResponse)request.GetResponse())
			{
				var ms = new MemoryStream();
				response.GetResponseStream().CopyTo(ms);

				try
				{
					ms.Position = 0;
					return JsonHelper.ParseJson<Election>(ms);
				}
				catch(Exception e)
				{
					throw new ServiceException(ExitCode.MUMBLE, "Failed to parse 'startElection' response (expected Election)\n" + e);
				}
			}
		}

		public static PrivateKey Nominate(string host, int port, CookieCollection cookieCollection, Guid electionId)
		{
			var request = CreateRequest(string.Format("http://{0}:{1}/nominate", host, port), WebRequestMethods.Http.Post, cookieCollection);

			var data = Encoding.UTF8.GetBytes(string.Format("electionId={0}", HttpUtility.UrlEncode(electionId.ToString())));
			using(var requestStream = request.GetRequestStream())
				requestStream.Write(data, 0, data.Length);

			using(var response = (HttpWebResponse)request.GetResponse())
			{
				var ms = new MemoryStream();
				response.GetResponseStream().CopyTo(ms);

				try
				{
					ms.Position = 0;
					return JsonHelper.ParseJson<PrivateKey>(ms);
				}
				catch(Exception e)
				{
					throw new ServiceException(ExitCode.MUMBLE, "Failed to parse 'nominate' response (expected PrivateKey)\n" + e);
				}
			}
		}

		public static void Vote(string host, int port, CookieCollection cookieCollection, Guid electionId, BigInteger[] encryptedVector)
		{
			var request = CreateRequest(string.Format("http://{0}:{1}/vote", host, port), WebRequestMethods.Http.Post, cookieCollection);

			var data = Encoding.UTF8.GetBytes(string.Format("electionId={0}&vote={1}", HttpUtility.UrlEncode(electionId.ToString()), HttpUtility.UrlEncode(encryptedVector.Select(integer => integer.ToString()).ToArray().ToJsonString())));
			using(var requestStream = request.GetRequestStream())
				requestStream.Write(data, 0, data.Length);

			
			using(var response = (HttpWebResponse)request.GetResponse())
			{
			}
		}

		public static Election FindElection(string host, int port, CookieCollection cookieCollection, Guid electionId)
		{
			var request = CreateRequest(string.Format("http://{0}:{1}/findElection?id={2}", host, port, electionId), WebRequestMethods.Http.Get, cookieCollection);

			using(var response = (HttpWebResponse)request.GetResponse())
			{
				var ms = new MemoryStream();
				response.GetResponseStream().CopyTo(ms);

				try
				{
					ms.Position = 0;
					return JsonHelper.ParseJson<Election>(ms);
				}
				catch(Exception e)
				{
					throw new ServiceException(ExitCode.MUMBLE, "Failed to parse 'findElection' response (expected Election)\n" + e);
				}
			}
		}

		private static HttpWebRequest CreateRequest(string url, string method = WebRequestMethods.Http.Get, CookieCollection cookieCollection = null)
		{
			var request = (HttpWebRequest)WebRequest.Create(url);
			request.Method = method;
			request.Timeout = 5000;
			request.KeepAlive = true;
			request.Proxy = null;
			request.ServicePoint.UseNagleAlgorithm = false;
			request.ServicePoint.ConnectionLimit = 150;
			request.ServicePoint.Expect100Continue = false;
			request.CookieContainer = new CookieContainer();
			if(cookieCollection != null)
				request.CookieContainer.Add(cookieCollection);
			return request;
		}
	}
}
