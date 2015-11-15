using System.Net;
using System.Web;
using Electro.Model;
using Electro.Utils;

namespace Electro.Handlers
{
	internal abstract class AuthorizedBaseHandler : BaseHttpHandler
	{
		private readonly AuthController authController;

		protected AuthorizedBaseHandler(AuthController authController, string prefix) : base(prefix)
		{
			this.authController = authController;
		}

		protected override void ProcessRequest(HttpListenerContext context)
		{
			var cookie = context.Request.Cookies[RegisterHandler.TokenCookieName];
			if(cookie == null || string.IsNullOrEmpty(cookie.Value))
			{
				ProcessUnauthorizedRequest(context);
				return;
			}

			var token = CommonUtils.TryOrDefault(() => JsonHelper.ParseJson<Token>(TokenCrypt.Decrypt(HttpUtility.UrlDecode(cookie.Value))));
			if(token == null)
			{
				ProcessForbiddenRequest(context);
				return;
			}
			var user = authController.FindUser(token.Login);
			if(user == null)
			{
				ProcessUserNotFoundRequest(context);
				return;
			}

			ProcessAuthorizedRequest(context, user);
		}

		protected abstract void ProcessAuthorizedRequest(HttpListenerContext context, User user);

		protected virtual void ProcessUnauthorizedRequest(HttpListenerContext context)
		{
			throw new HttpException(HttpStatusCode.Unauthorized, "Not authorized");
		}

		protected virtual void ProcessForbiddenRequest(HttpListenerContext context)
		{
			throw new HttpException(HttpStatusCode.Forbidden, "Invalid credentials");
		}

		private void ProcessUserNotFoundRequest(HttpListenerContext context)
		{
			throw new HttpException(HttpStatusCode.Forbidden, "Can't find user with provided credentials");
		}
	}
}