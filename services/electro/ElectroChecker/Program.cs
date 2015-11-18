using System;
using System.Net;
using log4net;
using log4net.Config;

namespace ElectroChecker
{
	static class Program
	{
		private static void GetCommonParams(string[] args, out string host, out string id, out string flag, out int vuln)
		{
			vuln = 0;
			if(args.Length < 5 || !int.TryParse(args[4], out vuln) || vuln < 1)
				ExitWithMessage(ExitCode.CHECKER_ERROR, "Invalid args");
			host = args[1];
			id = args[2];
			flag = args[3];
		}

		public static void Main(string[] args)
		{
			XmlConfigurator.Configure();
			try
			{
				if(args.Length < 1)
					ExitWithMessage(ExitCode.CHECKER_ERROR, "Not enough args");

				var mode = args[0].ToLower();
				try
				{
					switch(mode)
					{
						case CommandInfo:
							ExitWithMessage(ExitCode.OK, null, "vulns: 1:1");
							break;
						case CommandCheck:
							ExitWithMessage(ExitCode.OK, "No check needed in this service");
							break;
						case CommandPut:
							ProcessPut(args);
							break;
						case CommandGet:
							ProcessGet(args);
							break;
					}
				}
				catch(WebException e)
				{
					if(e.Status == WebExceptionStatus.ConnectFailure)
					{
						var mes = string.Format("Connection failure in '{0}' mode", mode);
						ExitWithMessage(ExitCode.DOWN, mes, mes);
					}
					if(e.Status == WebExceptionStatus.Timeout)
					{
						var mes = string.Format("Timeout in '{0}' mode", mode);
						ExitWithMessage(ExitCode.DOWN, mes, mes);
					}
					if(e.Status == WebExceptionStatus.NameResolutionFailure)
					{
						var mes = string.Format("NameResolutionFailure in '{0}' mode", mode);
						ExitWithMessage(ExitCode.DOWN, mes, mes);
					}
					ExitWithMessage(ExitCode.MUMBLE, e.ToString());
				}
				catch(ServiceException se)
				{
					ExitWithMessage(se.code, se.ToString());
				}
			}
			catch(Exception e)
			{
				ExitWithMessage(ExitCode.CHECKER_ERROR, e.ToString());
			}
		}

		private static void ProcessPut(string[] args)
		{
			string host, id, flag;
			int vuln;
			GetCommonParams(args, out host, out id, out flag, out vuln);

			if(vuln == 1)
				Vuln1Methods.ProcessPut(host, id, flag);
			else if(vuln == 2)
				Vuln2Methods.ProcessPut(host, id, flag);
			else
				ExitWithMessage(ExitCode.CHECKER_ERROR, string.Format("Unsupported vuln #{0}", vuln));
		}

		private static void ProcessGet(string[] args)
		{
			string host, id, flag;
			int vuln;
			GetCommonParams(args, out host, out id, out flag, out vuln);

			if(vuln == 1)
				Vuln1Methods.ProcessGet(host, id, flag);
			else if(vuln == 2)
				Vuln2Methods.ProcessGet(host, id, flag);
			else
				ExitWithMessage(ExitCode.CHECKER_ERROR, string.Format("Unsupported vuln #{0}", vuln));
		}

		
		public static void ExitWithMessage(ExitCode exitCode, string stderr, string stdout = null)
		{
			if (stdout != null)
				Console.WriteLine(stdout);
			if(stderr != null)
			{
				if(exitCode == ExitCode.OK)
					log.InfoFormat(stderr);
				else
					log.ErrorFormat(stderr);
			}

			Environment.Exit((int) exitCode);
		}

		public const int PORT = 3130;

		private const string CommandInfo = "info";
		private const string CommandCheck = "check";
		private const string CommandPut = "put";
		private const string CommandGet = "get";

		private static readonly ILog log = LogManager.GetLogger(typeof(Program));
	}
}
