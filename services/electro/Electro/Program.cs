using System;
using System.IO;
using System.Threading;
using Electro.Handlers;
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

				var startElectionHandler = new StartElectionHandler(electroController, authController, GetPrefix("startElection"));
				startElectionHandler.Start();

				var listElectionsHandler = new ListElectionsHandler(electroController, GetPrefix("listElections"));
				listElectionsHandler.Start();

				var findElectionHandler = new FindElectionHandler(electroController, GetPrefix("findElection"));
				findElectionHandler.Start();

				var nominateHandler = new NominateHandler(electroController, authController, GetPrefix("nominate"));
				nominateHandler.Start();

				var voteHandler = new VoteHandler(electroController, authController, GetPrefix("vote"));
				voteHandler.Start();

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
