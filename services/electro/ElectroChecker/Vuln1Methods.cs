using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Electro.Crypto;
using Electro.Utils;

namespace ElectroChecker
{
	static class Vuln1Methods
	{
		//TODO give more time 
		const int nominateTimeInSec = 2;
		const int voteTimeInSec = 5;

		const int candidatesCount = 2;

		public static void ProcessPut(string host, string id, string flag)
		{
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
				candidate.Cookies = ElectroClient.RegUser(host, Program.PORT, candidate.Login, candidate.Pass, candidate.PublicMessage, candidate.PrivateMessage);
				candidates.Add(candidate);
			}

			var election = ElectroClient.StartElection(host, Program.PORT, candidates[0].Cookies, Utils.GenRandomElectionName(), true, nominateTimeInSec, voteTimeInSec);
			if(election == null)
				throw new ServiceException(ExitCode.MUMBLE, "Can't start election - result is NULL");
			var electionStartDt = DateTime.UtcNow;

			foreach(var candidate in candidates.Skip(1))
			{
				ElectroClient.Nominate(host, Program.PORT, candidate.Cookies, election.Id);
			}

			Thread.Sleep(nominateTimeInSec * 1000);

			for(int i = 0; i < candidates.Count; i++)
			{
				var candidate = candidates[i];
				var vote = Utils.GenVoteVector(candidatesCount, i);
				ElectroClient.Vote(host, Program.PORT, candidate.Cookies, election.Id, HomoCrypto.EncryptVector(vote, election.PublicKey));
				expectedResult.AddVoteVector(vote);
			}

			var voters = new List<User>();
			foreach(var voteVector in votes)
			{
				var voter = UsersManager.GenRandomUser();
				voter.Cookies = ElectroClient.RegUser(host, Program.PORT, voter.Login, voter.Pass);
				voters.Add(voter);

				ElectroClient.Vote(host, Program.PORT, voter.Cookies, election.Id, HomoCrypto.EncryptVector(voteVector, election.PublicKey));
				expectedResult.AddVoteVector(voteVector);
			}

			var state = new Vuln1State
			{
				ElectionStartDate = electionStartDt,
				ElectionId = election.Id.ToString(),
				Candidates = candidates.ToArray(),
				expectedResult = expectedResult
			};

			Program.ExitWithMessage(ExitCode.OK, null, Convert.ToBase64String(Encoding.UTF8.GetBytes(state.ToJsonString())));
		}

		public static void ProcessGet(string host, string id, string flag)
		{
			var state = JsonHelper.ParseJson<Vuln1State>(Convert.FromBase64String(id));

			var now = DateTime.UtcNow;
			var elapsedSeconds = now.Subtract(state.ElectionStartDate).TotalMilliseconds;
			if(elapsedSeconds < 0)
				throw new ServiceException(ExitCode.CHECKER_ERROR, string.Format("Possible time desynchronization on checksystem hosts! Election started in future: '{0}' and now is only '{1}'", state.ElectionStartDate.ToSortable(), now.ToSortable()));
			var tts = (nominateTimeInSec + voteTimeInSec + 1) * 1000 - elapsedSeconds;
			if(tts > 0)
			{
				Console.Error.WriteLine("Sleeping for {0} seconds (Election start '{1}' now '{2}' nomination duration {3} vote duration {4})", tts, state.ElectionStartDate.ToSortable(), now.ToSortable(), nominateTimeInSec, voteTimeInSec);
				Thread.Sleep((int) tts);
			}

			var expectedResult = state.expectedResult;
			var expectedWinnerNum = Utils.FindWinner(expectedResult);

			var candidates = state.Candidates;
			var expectedWinner = candidates[expectedWinnerNum];

			var election = ElectroClient.FindElection(host, Program.PORT, expectedWinner.Cookies, state.ElectionId);

			var readlWinner = election.FindWinner();
			if(readlWinner == null)
				throw new ServiceException(ExitCode.MUMBLE, string.Format("Can't find winner in election '{0}'", election.Id));
			if(readlWinner.Name != expectedWinner.Login)
				throw new ServiceException(ExitCode.MUMBLE, string.Format("Winner in election '{0}' is wrong. Expected '{1}' got '{2}", election.Id, expectedWinner.Login, readlWinner.Name));

			if(election.Candidates.All(info => info.PrivateNotesForWinner != flag))
				throw new ServiceException(ExitCode.CORRUPT, "Can't find flag", null);

			Program.ExitWithMessage(ExitCode.OK, "Flag found! OK", null);
		}
	}
}
