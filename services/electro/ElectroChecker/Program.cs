using System;
using System.Net;
using log4net;
using log4net.Config;

namespace ElectroChecker
{
	static class Program
	{
		private static int GetCommonParams(string[] args, out string host, out string id, out string flag, out int vuln)
		{
			host = null;
			id = null;
			flag = null;
			vuln = 0;
			if(args.Length < 5 || !int.TryParse(args[4], out vuln) || vuln < 1)
				return ExitWithMessage(ExitCode.CHECKER_ERROR, "Invalid args");
			host = args[1];
			id = args[2];
			flag = args[3];
			return (int) ExitCode.OK;
		}

		public static int Main(string[] args)
		{
			XmlConfigurator.Configure();
			try
			{
				if(args.Length < 1)
					return ExitWithMessage(ExitCode.CHECKER_ERROR, "Not enough args");

				var mode = args[0].ToLower();
				try
				{
					switch(mode)
					{
						case CommandInfo:
							return ExitWithMessage(ExitCode.OK, null, "vulns: 1:1");
						case CommandCheck:
							return ExitWithMessage(ExitCode.OK, "No check needed in this service");
						case CommandPut:
							return ProcessPut(args);
						case CommandGet:
							return ProcessGet(args);
					}
				}
				catch(WebException e)
				{
					if(e.Status == WebExceptionStatus.ConnectFailure)
					{
						var mes = string.Format("Connection failure in '{0}' mode", mode);
						return ExitWithMessage(ExitCode.DOWN, mes, mes);
					}
					if(e.Status == WebExceptionStatus.Timeout)
					{
						var mes = string.Format("Timeout in '{0}' mode", mode);
						return ExitWithMessage(ExitCode.DOWN, mes, mes);
					}
					if(e.Status == WebExceptionStatus.NameResolutionFailure)
					{
						var mes = string.Format("NameResolutionFailure in '{0}' mode", mode);
						return ExitWithMessage(ExitCode.DOWN, mes, mes);
					}
					return ExitWithMessage(ExitCode.MUMBLE, e.ToString());
				}
				catch(ServiceException se)
				{
					return ExitWithMessage(se.code, se.ToString());
				}
			}
			catch(Exception e)
			{
				return ExitWithMessage(ExitCode.CHECKER_ERROR, e.ToString());
			}
			return (int) ExitCode.OK;
		}

		private static int ProcessPut(string[] args)
		{
			string host, id, flag;
			int vuln;

			int ec;
			if((ec = GetCommonParams(args, out host, out id, out flag, out vuln)) != (int) ExitCode.OK)
				return ec;

			if(vuln == 1)
				return Vuln1Methods.ProcessPut(host, id, flag);
			else if(vuln == 2)
				return Vuln2Methods.ProcessPut(host, id, flag);
			else
				return ExitWithMessage(ExitCode.CHECKER_ERROR, string.Format("Unsupported vuln #{0}", vuln));
		}

		private static int ProcessGet(string[] args)
		{
			string host, id, flag;
			int vuln;
			GetCommonParams(args, out host, out id, out flag, out vuln);

			if(vuln == 1)
				return Vuln1Methods.ProcessGet(host, id, flag);
			else if(vuln == 2)
				return Vuln2Methods.ProcessGet(host, id, flag);
			else
				return ExitWithMessage(ExitCode.CHECKER_ERROR, string.Format("Unsupported vuln #{0}", vuln));
		}

		
		public static int ExitWithMessage(ExitCode exitCode, string stderr, string stdout = null)
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

			return (int)exitCode;
		}

		public const int PORT = 80;

		private const string CommandInfo = "info";
		private const string CommandCheck = "check";
		private const string CommandPut = "put";
		private const string CommandGet = "get";

		private static readonly ILog log = LogManager.GetLogger(typeof(Program));
	}
}
