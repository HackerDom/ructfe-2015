using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Numerics;
using System.Threading;
using Electro.Handlers;
using Electro.Model;
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
				ThreadPool.SetMinThreads(32, 1024);

				var statePersister = new StatePersister();

				AuthController authController = new AuthController(StatePersister.LoadUsers(), statePersister);
				ElectroController electroController = new ElectroController(StatePersister.LoadElections(), StatePersister.LoadKeys(), authController, statePersister);

				var staticHandler = new StaticHandler(GetPrefix(null), Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "web"));
				staticHandler.Start();

				var registerHandler = new RegisterHandler(authController, GetPrefix("register"));
				registerHandler.Start();

				var loginHandler = new LoginHandler(authController, GetPrefix("login"));
				loginHandler.Start();

				var logoutHandler = new LogoutHandler(authController, GetPrefix("logout"));
				logoutHandler.Start();

				var startElectionHandler = new StartElectionHandler(electroController, authController, GetPrefix("startElection"));
				startElectionHandler.Start();

				var listElectionsHandler = new ListElectionsHandler(electroController, authController, GetPrefix("listElections"));
				listElectionsHandler.Start();

				var findElectionHandler = new FindElectionHandler(electroController, authController, GetPrefix("findElection"));
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
