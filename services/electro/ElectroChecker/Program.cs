using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading;
using Electro.Crypto;
using Electro.Model;
using Electro.Utils;

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
						ExitWithMessage(ExitCode.OK, null, "2");
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

		private static void ProcessPut(string[] args)
		{
			string host, id, flag;
			int vuln;
			GetCommonParams(args, out host, out id, out flag, out vuln);

			if(vuln == 1)
				ProcessPut1(host, id, flag);
			else
				ExitWithMessage(ExitCode.CHECKER_ERROR, string.Format("Unsupported vuln #{0}", vuln));
		}

		private static void ProcessGet(string[] args)
		{
			string host, id, flag;
			int vuln;
			GetCommonParams(args, out host, out id, out flag, out vuln);

			if(vuln == 1)
				ProcessGet1(host, id, flag);
			else
				ExitWithMessage(ExitCode.CHECKER_ERROR, string.Format("Unsupported vuln #{0}", vuln));
		}

		private static void ProcessPut1(string host, string id, string flag)
		{
			//TODO give more time 
			int nominateTimeInSec = 2;
			int voteTimeInSec = 4;

			int candidatesCount = 2;

			var votes = Utils.GenRandomVoteVectors(candidatesCount, 3, 5).ToList();
			var expectedResult = Utils.SumVoteVectors(votes);
			var winnerNum = Utils.FindWinner(expectedResult);

			var flagSent = false;
			var candidates = new List<User>();
			for(int i = 0; i < candidatesCount; i++)
			{
				string privateNotes = null;
				if(!flagSent && i != winnerNum)
				{
					privateNotes = flag;
					flagSent = true;
				}

				var candidate = UsersManager.GenRandomUser(privateNotes);
				candidate.Cookies = ElectroClient.RegUser(host, PORT, candidate.Login, candidate.Pass, candidate.PublicMessage, candidate.PrivateMessage);
				candidates.Add(candidate);
			}

			var electionStartDt = DateTime.UtcNow;

			var election = ElectroClient.StartElection(host, PORT, candidates[0].Cookies, "Election_" + Utils.GenRandomAlphaNumeric(8, 8), true, nominateTimeInSec, voteTimeInSec);
			foreach(var candidate in candidates.Skip(1))
			{
				ElectroClient.Nominate(host, PORT, candidate.Cookies, election.Id);
			}

			Thread.Sleep(nominateTimeInSec * 1000);

			for(int i = 0; i < candidates.Count; i++)
			{
				var candidate = candidates[i];
				var vote = Utils.GenVoteVector(candidatesCount, i);
				ElectroClient.Vote(host, PORT, candidate.Cookies, election.Id, HomoCrypto.EncryptVector(vote, election.PublicKey));
				expectedResult.AddVoteVector(vote);
			}

			var voters = new List<User>();
			foreach(var voteVector in votes)
			{
				var voter = UsersManager.GenRandomUser();
				voter.Cookies = ElectroClient.RegUser(host, PORT, voter.Login, voter.Pass);
				voters.Add(voter);

				ElectroClient.Vote(host, PORT, voter.Cookies, election.Id, HomoCrypto.EncryptVector(voteVector, election.PublicKey));
				expectedResult.AddVoteVector(voteVector);
			}

			var state = new IdState1
			{
				ElectionStartDate = electionStartDt,
				ElectionId = election.Id,
				Candidates = candidates.ToArray(),
				Voters = voters.ToArray(),
				expectedResult = expectedResult
			};

			ExitWithMessage(ExitCode.OK, Convert.ToBase64String(Encoding.UTF8.GetBytes(state.ToJsonString())));
		}

		private static void ProcessGet1(string host, string id, string flag)
		{
			var state = JsonHelper.ParseJson<IdState1>(Convert.FromBase64String(id));

			var expectedResult = state.expectedResult;
			var expectedWinnerNum = Utils.FindWinner(expectedResult);

			var candidates = state.Candidates;
			var expectedWinner = candidates[expectedWinnerNum];

			var election = ElectroClient.FindElection(host, PORT, expectedWinner.Cookies, state.ElectionId);

			var readlWinner = election.FindWinner();
			if(readlWinner == null)
				ExitWithMessage(ExitCode.MUMBLE, string.Format("Can't find winner in election '{0}'", election.Id));
			if(readlWinner.Name != expectedWinner.Login)
				ExitWithMessage(ExitCode.MUMBLE, string.Format("Winner in election '{0}' is wrong. Expected '{1}' got '{2}", election.Id, expectedWinner.Login, readlWinner.Name));

			if(election.Candidates.All(info => info.PrivateNotesForWinner != flag))
				ExitWithMessage(ExitCode.CORRUPT, "Can't find flag", null);

			ExitWithMessage(ExitCode.OK, "Flag found", null);
		}

		private static void ExitWithMessage(ExitCode exitCode, string stderr, string stdout = null)
		{
			if (stdout != null)
				Console.WriteLine(stdout);
			if (stderr != null)
				Console.Error.WriteLine(stderr);
			Environment.Exit((int) exitCode);
		}

		private const int PORT = 3130;

		private const string CommandInfo = "info";
		private const string CommandCheck = "check";
		private const string CommandPut = "put";
		private const string CommandGet = "get";
	}
}
