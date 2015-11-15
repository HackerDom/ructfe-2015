using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Web;
using Electro.Utils;

namespace Electro.Handlers
{
	internal static class HttpListenerUtils
	{
		public static void AssertMethod(this HttpListenerRequest request, string method)
		{
			if(request.HttpMethod != method)
				throw new HttpException(HttpStatusCode.MethodNotAllowed, string.Format("Only {0} method is allowed", method));
		}

		public static Dictionary<string, string> GetPostData(this HttpListenerRequest request)
		{
			using(var ms = new MemoryStream())
			{
				request.InputStream.CopyTo(ms);
				var data = Encoding.UTF8.GetString(ms.GetBuffer(), 0, (int)ms.Length);
				return data.Split('&').Select(pair => pair.Split('=')).Where(pair => pair.Length == 2).ToDict(pair => HttpUtility.UrlDecode(pair[0]), pair => HttpUtility.UrlDecode(pair[1]));
			}
		}
	}
}