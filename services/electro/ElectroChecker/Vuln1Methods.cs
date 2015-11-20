using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Electro.Crypto;
using Electro.Utils;
using log4net;

namespace ElectroChecker
{
	static class Vuln1Methods
	{
		//TODO give more time 
		const int nominateTimeInSec = 60;
		const int voteTimeInSec = 8 * 60;

		const int candidatesMinCount = 2;
		const int candidatesMaxCount = 5;

		const int votesMinCount = candidatesMaxCount + 1;
		const int votesMaxCount = votesMinCount * 2;

		private static User[] GenerateCandidates(int minCount, int maxCount)
		{
			var r = new Random();
			int count = r.Next(minCount, maxCount + 1);
			return Enumerable.Range(0, count).Select(i => UsersManager.GenRandomUser()).ToArray();
		}

		public static int ProcessPut(string host, string id, string flag)
		{
			log.Info("Processing Vuln1.Put");

			var r = new Random();
			var candidateUsers = GenerateCandidates(candidatesMinCount, candidatesMaxCount);
			var candidateWithFlagNum = r.Next(candidateUsers.Length);
			var candidateWithFlag = candidateUsers[candidateWithFlagNum];
			candidateWithFlag.PrivateMessage = flag;
			log.InfoFormat("Generated {0} candidates (#{1} has flag)", candidateUsers.Length, candidateWithFlagNum);

			candidateUsers = Vuln2Methods.RegisterCandidates(host, candidateUsers).OrderBy(user => user.Login).ToArray();
			var election = Vuln2Methods.StartElection(host, candidateUsers[0], true, nominateTimeInSec, voteTimeInSec);
			var electionStartDt = DateTime.UtcNow;

			Vuln2Methods.NominateUsers(host, election, candidateUsers.Skip(1).ToArray());

			var state = new Vuln1State
			{
				ElectionStartDate = electionStartDt,
				NominateTimeInSec = nominateTimeInSec,
				VoteTimeInSec = voteTimeInSec,
				ElectionId = election.Id.ToString(),
				Candidates = candidateUsers
			};

			log.Info("Flag put");
			Console.Out.WriteLine(Convert.ToBase64String(Encoding.UTF8.GetBytes(state.ToJsonString())));
			return (int) ExitCode.OK;
		}

		public static int ProcessGet(string host, string id, string flag)
		{
			log.Info("Processing Vuln1.Get");

			var state = JsonHelper.ParseJson<Vuln1State>(Convert.FromBase64String(id));

			var now = DateTime.UtcNow;
			var elapsedSeconds = now.Subtract(state.ElectionStartDate).TotalMilliseconds;
			if(elapsedSeconds < 0)
				throw new ServiceException(ExitCode.CHECKER_ERROR, string.Format("Possible time desynchronization on checksystem hosts! Election started in future: '{0}' and now is only '{1}'", state.ElectionStartDate.ToSortable(), now.ToSortable()));

			var nominateEndTime = state.ElectionStartDate.AddSeconds(nominateTimeInSec);
			var voteEndTime = state.ElectionStartDate.AddSeconds(nominateTimeInSec + voteTimeInSec);

			log.InfoFormat("Looking for Election {0}", state.ElectionId);
			var election = ElectroClient.FindElection(host, Program.PORT, state.Candidates[0].Cookies, state.ElectionId);
			if(election == null || election.Candidates == null || election.Candidates.Count < 2)
				throw new ServiceException(ExitCode.CORRUPT, string.Format("Can't find election '{0}' or it has less than 2 candidates", state.ElectionId));
			log.InfoFormat("Election {0} found", state.ElectionId);

			log.InfoFormat("Election startDt {0}", state.ElectionStartDate.ToSortable());
			log.InfoFormat("Nominate end Dt  {0}", nominateEndTime.ToSortable());
			log.InfoFormat("Vote end Dt      {0}", voteEndTime.ToSortable());
			log.InfoFormat("Now              {0}", now.ToSortable());

			if(now < nominateEndTime)
			{
				log.InfoFormat("Nomination is still going, got election, considering everything OK");
				return (int)ExitCode.OK;
			}
			else if(now < voteEndTime)
			{
				log.InfoFormat("Nomination finished, but voting is still going. Trying to win!");
				int notFlagNum = 0;
				for(; notFlagNum < election.Candidates.Count; notFlagNum++)
				{
					if(election.Candidates[notFlagNum] != null && !election.Candidates[notFlagNum].IsMe)
						break;
				}
				if(notFlagNum == election.Candidates.Count)
					throw new ServiceException(ExitCode.CORRUPT, string.Format("Can't find candidate with no flag in election '{0}'", state.ElectionId));

				var random = new Random();
				var votersCount = random.Next(votesMinCount, votesMaxCount + 1);

				var votesForWinner =
					Enumerable.Repeat(Utils.GenVoteVector(election.Candidates.Count, notFlagNum), (votersCount/2) + 1).ToArray();
				var restVotes = Utils.GenRandomVoteVectors(election.Candidates.Count, votersCount - votesForWinner.Length).ToArray();
				var votes = votesForWinner.Concat(restVotes).ToArray();

				var voters = Vuln2Methods.RegisterVoters(host, votes, state.Candidates);
				Vote(host, voters, election.Id, election.PublicKey);
				return (int)ExitCode.OK;
			}
			else
			{
				log.InfoFormat("Voting has already finished. Considering everything OK");
				var realWinner = election.FindWinner();
				if(realWinner == null)
					throw new ServiceException(ExitCode.MUMBLE, string.Format("Can't find winner in election '{0}'", election.Id));

				var winner = state.Candidates.FirstOrDefault(info => info.Login == realWinner.Name);
				if(winner == null)
					throw new ServiceException(ExitCode.CORRUPT, string.Format("We have no credentials for winner in election '{0}'. Possibly hacker won, so we lost a flag", election.Id));

				log.InfoFormat("Reloading election, now as winner '{0}'", winner.Login);
				election = ElectroClient.FindElection(host, Program.PORT, winner.Cookies, election.Id.ToString());
				if(election == null)
					throw new ServiceException(ExitCode.CORRUPT, string.Format("Can't find election '{0}'", state.ElectionId));

				if(election.Candidates.All(info => info.PrivateNotesForWinner != flag))
					throw new ServiceException(ExitCode.CORRUPT, "Can't find flag", null);

				log.Info("Flag found! Ok");
				return (int)ExitCode.OK;
			}
		}

		private static void Vote(string host, KeyValuePair<User, int[]>[] voters, Guid id, PublicKey publicKey)
		{
			log.Info("Voting in parallel...");
			var candidateTasks = voters.Select(kvp => ElectroClient.VoteAsync(host, Program.PORT, kvp.Key.Cookies, id, HomoCrypto.EncryptVector(kvp.Value, publicKey))).ToArray();
			try
			{
				Task.WaitAll();
				log.InfoFormat("Voted by {0} users", voters.Length);
			}
			catch(Exception e)
			{
				throw new ServiceException(ExitCode.DOWN, string.Format("Failed to vote by {0} users in parallel: {1}", candidateTasks.Length, e));
			}
		}

		private static readonly ILog log = LogManager.GetLogger(typeof(Vuln1Methods));
	}
}
