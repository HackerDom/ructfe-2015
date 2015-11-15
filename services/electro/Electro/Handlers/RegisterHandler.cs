using System;
using System.Net;
using System.Text.RegularExpressions;
using Electro.Model;
using Electro.Utils;

namespace Electro.Handlers
{
	public class RegisterHandler : BaseHttpHandler
	{
		private readonly AuthController authController;

		public RegisterHandler(AuthController authController, string prefix) : base(prefix)
		{
			this.authController = authController;
		}

		protected override void ProcessRequest(HttpListenerContext context)
		{
			context.Request.AssertMethod(WebRequestMethods.Http.Post);
			var form = context.Request.GetPostData();

			string login, pass;
			if(!form.TryGetValue("login", out login) || string.IsNullOrEmpty(login))
				throw new HttpException(HttpStatusCode.BadRequest, "Empty 'login' value");

			if(!form.TryGetValue("pass", out pass) || string.IsNullOrEmpty(pass))
				throw new HttpException(HttpStatusCode.BadRequest, "Empty 'pass' value");

			if(login.Length > MaxLength || pass.Length > MaxLength)
				throw new HttpException(HttpStatusCode.BadRequest, string.Format("Too large login/pass (max len {0})", MaxLength));

			if(!Regex.IsMatch(login, @"^\w+$"))
				throw new HttpException(HttpStatusCode.BadRequest, @"Only \w chars allowed in login");

			User user;
			if((user = authController.AddUser(login, pass)) == null)
				throw new HttpException(HttpStatusCode.Conflict, string.Format("User '{0}' already exists", login));

			context.Response.SetCookie(LoginCookieName, login);
			context.Response.SetCookie(TokenCookieName, TokenCrypt.Encrypt(new Token { Login = login }.ToJsonString()), true);

			WriteString(context, "Register OK");
		}

		public const string TokenCookieName = "authtoken";
		public const string LoginCookieName = "login";

		private const int MaxLength = 64;
	}
}