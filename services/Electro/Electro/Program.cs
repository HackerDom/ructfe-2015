using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Electro.Handlers;
using Electro.Utils;
using log4net;
using log4net.Config;

namespace Electro
{
	class Program
	{
		static void Main(string[] args)
		{
			XmlConfigurator.Configure();
			try
			{
				AuthController authController = new AuthController();
				ElectroController electroController = new ElectroController();

				var staticHandler = new StaticHandler(GetPrefix("static"), Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "static"));
				staticHandler.Start();

				var registerHandler = new RegisterHandler(authController, GetPrefix("register"));
				registerHandler.Start();

				var loginHandler = new LoginHandler(authController, GetPrefix("login"));
				loginHandler.Start();

				Thread.Sleep(Timeout.Infinite);
			}
			catch(Exception e)
			{
				log.Fatal(e);
			}
		}

		private static string GetPrefix(string suffix)
		{
			return string.Format("http://+:{0}/{1}", Port, suffix == null ? null : suffix.TrimEnd('/') + '/');
		}

		private const int Port = 3130;

		private static readonly ILog log = LogManager.GetLogger(typeof(Program));
	}
}
