using System;
using System.Net;
using Electro.Model;
using Electro.Utils;

namespace Electro.Handlers
{
	internal class LoginHandler : BaseHttpHandler
	{
		private readonly AuthController authController;

		public LoginHandler(AuthController authController, string prefix) : base(prefix)
		{
			this.authController = authController;
		}

		protected override void ProcessRequest(HttpListenerContext context)
		{
			context.Request.AssertMethod(WebRequestMethods.Http.Post);
			var form = context.Request.GetPostData();

			User user;
			string login, pass;
			if(!form.TryGetValue("login", out login) || !form.TryGetValue("pass", out pass) || string.IsNullOrEmpty(login) || string.IsNullOrEmpty(pass) || (user = authController.FindUser(login, pass)) == null)
				throw new HttpException(HttpStatusCode.Forbidden, "Invalid credentials");

			context.Response.SetCookie("login", login);
			context.Response.SetCookie("token", TokenCrypt.Encrypt(new Token { Login = login }.ToJsonString()), true);

			WriteString(context, "Name OK");
		}
	}
}