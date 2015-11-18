using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;

namespace Electro.Handlers
{
	class LogoutHandler : BaseHttpHandler
	{
		private readonly AuthController authController;

		public LogoutHandler(AuthController authController, string prefix) : base(prefix)
		{
			this.authController = authController;
		}

		protected override void ProcessRequest(HttpListenerContext context)
		{
			context.Response.SetCookie(new Cookie(RegisterHandler.LoginCookieName, null) { Expires = DateTime.Now.AddDays(-1)});
			context.Response.SetCookie(new Cookie(RegisterHandler.TokenCookieName, null) {Expires = DateTime.Now.AddDays(-1), HttpOnly = true});

			WriteString(context, "Logout OK");
		}
	}
}
