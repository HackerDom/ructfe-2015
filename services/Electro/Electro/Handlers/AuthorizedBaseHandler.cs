using System.Net;
using System.Web;
using Electro.Utils;

namespace Electro.Handlers
{
	internal abstract class AuthorizedBaseHandler : BaseHttpHandler
	{
		protected AuthorizedBaseHandler(string prefix)
			: base(prefix)
		{
		}

		protected override void ProcessRequest(HttpListenerContext context)
		{
			var cookie = context.Request.Cookies[TokenCookieName];
			if(cookie == null || string.IsNullOrEmpty(cookie.Value))
			{
				ProcessUnauthorizedRequest(context);
				return;
			}

			var token = CommonUtils.TryOrDefault(() => Token.ParseJson(TokenCrypt.Decrypt(HttpUtility.UrlDecode(cookie.Value))));
			if(token == null)
			{
				ProcessForbiddenRequest(context);
				return;
			}

			ProcessAuthorizedRequest(context, token.Login);
		}

		protected abstract void ProcessAuthorizedRequest(HttpListenerContext context, string login);

		protected virtual void ProcessUnauthorizedRequest(HttpListenerContext context)
		{
			throw new HttpException(HttpStatusCode.Unauthorized, "Not authorized");
		}

		protected virtual void ProcessForbiddenRequest(HttpListenerContext context)
		{
			throw new HttpException(HttpStatusCode.Forbidden, "Invalid credentials");
		}

		private const string TokenCookieName = "authtoken";
	}
}