using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Threading;
using Electro.Crypto;

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
			if (args.Length < 1)
				ExitWithMessage(ExitCode.CHECKER_ERROR, "Not enough args");

			var mode = args[0].ToLower();

			try
			{
				switch(mode)
				{
					case CommandInfo:
						ExitWithMessage(ExitCode.OK, null, "1:1");
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
			catch (WebException e)
			{
				if (e.Status == WebExceptionStatus.ConnectFailure)
				{
					var mes = string.Format("Connection failure in '{0}' mode", mode);
					ExitWithMessage(ExitCode.DOWN, mes, mes);
				}
				if (e.Status == WebExceptionStatus.Timeout)
				{
					var mes = string.Format("Timeout in '{0}' mode", mode);
					ExitWithMessage(ExitCode.DOWN, mes, mes);
				}
				ExitWithMessage(ExitCode.MUMBLE, e.ToString());
			}
			catch(Exception e)
			{
				ExitWithMessage(ExitCode.CHECKER_ERROR, e.ToString());
			}
		}

		private const int PORT = 3130;

		private static void ProcessPut(string[] args)
		{
			//TODO give more time 
			int nominateTimeInSec = 2;
			int voteTimeInSec = 4;


			string host, id, flag;
			int vuln;
			GetCommonParams(args, out host, out id, out flag, out vuln);

			var firstCandidate = GenRandomUser();
			var firstCandidateCookie = ElectroClient.RegUser(host, PORT, firstCandidate.Key, firstCandidate.Value);

			var secondCandidate = GenRandomUser();
			var secondCandidateCookie = ElectroClient.RegUser(host, PORT, secondCandidate.Key, secondCandidate.Value);

			var electionStartDt = DateTime.UtcNow;
			var election = ElectroClient.StartElection(host, PORT, firstCandidateCookie, "Election " + GenRandomAlphaNumeric(8), true, nominateTimeInSec, voteTimeInSec);
			ElectroClient.Nominate(host, PORT, secondCandidateCookie, election.Id);
			
			Thread.Sleep(nominateTimeInSec * 1000);

			ElectroClient.Vote(host, PORT, firstCandidateCookie, election.Id, HomoCrypto.EncryptVector(new [] {1, 0}, election.PublicKey));
			ElectroClient.Vote(host, PORT, secondCandidateCookie, election.Id, HomoCrypto.EncryptVector(new [] {0, 1}, election.PublicKey));
			var result = new[] { 1, 1 };

			int votersCount = 5;
			for(int i = 0; i < votersCount; i++)
			{
				var voter = GenRandomUser();
				var cookie = ElectroClient.RegUser(host, PORT, voter.Key, voter.Value);

				int[] voteVector = GenRandomVoteVector(2);
				ElectroClient.Vote(host, PORT, cookie, election.Id, HomoCrypto.EncryptVector(voteVector, election.PublicKey));
				result = SumVoteVectors(result, voteVector);
			}

			ExitWithMessage(ExitCode.OK, null);
		}

		private static int[] SumVoteVectors(int[] first, int[] second)
		{
			return first.Zip(second, (i, i1) => i + i1).ToArray();
		}

		private static int[] GenRandomVoteVector(int count)
		{
			var result = new int[count];
			result[random.Next(count)] = 1;
			return result;
		}

		

		private static void ProcessGet(string[] args)
		{
			string host, id, flag;
			int vuln;
			GetCommonParams(args, out host, out id, out flag, out vuln);
			
			ExitWithMessage(ExitCode.OK, null);
		}



		private static KeyValuePair<string, string> GenRandomUser()
		{
			var login = FullNames.NextFullName();
			string pass = GenRandomAlphaNumeric();
			return new KeyValuePair<string, string>(login, pass);
		}

		private static string GenRandomAlphaNumeric(int minLen = 6)
		{
			const string chars = "abcdefghijklmnopqrstuvwxyz0123456789";
			var len = minLen + random.Next(3);
			return string.Join("", Enumerable.Range(0, len).Select(i => chars[random.Next(0, chars.Length)]));
		}



		static Random random = new Random();

		private static void ExitWithMessage(ExitCode exitCode, string stderr, string stdout = null)
		{
			if (stdout != null)
				Console.WriteLine(stdout);
			if (stderr != null)
				Console.Error.WriteLine(stderr);
			Environment.Exit((int) exitCode);
		}

		private const string namesPath = "static/names";
		private const string surnamesPath = "static/surnames";

		private const string CommandInfo = "info";
		private const string CommandCheck = "check";
		private const string CommandPut = "put";
		private const string CommandGet = "get";
	}
}
