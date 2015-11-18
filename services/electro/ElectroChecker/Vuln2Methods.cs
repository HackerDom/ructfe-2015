using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net;
using System.Net.NetworkInformation;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Electro.Crypto;
using Electro.Model;
using Electro.Utils;
using log4net;

namespace ElectroChecker
{
	static class Vuln2Methods
	{
		const int nominateTimeInSec = 3;
		const int voteTimeInSec = 10;

		public static void ProcessPut(string host, string id, string flag)
		{
			log.Info("Processing Vuln2.Put");

			var candidateUsers = RegisterCandidates(host, flag.Distinct().Select(c => UsersManager.GenUser(null, c.ToString())).ToArray());

			var election = StartElection(host, candidateUsers[0]);

			var sw = Stopwatch.StartNew();
			election = NominateUsers(host, election, candidateUsers.Skip(1).ToArray());
			sw.Stop();

			var tts = nominateTimeInSec * 1000 - sw.ElapsedMilliseconds;
			if(tts > 0)
			{
				log.InfoFormat("Sleeping for {0}ms before voting (nomination duration is {1}s)", tts, nominateTimeInSec);
				Thread.Sleep((int) tts);
			}

			var votes = GenVotes(flag, election);

			var voters = RegisterVoters(host, votes, candidateUsers);

			log.InfoFormat("Voting by {0} voters", voters.Length);
			foreach(var voter in voters)
				ElectroClient.Vote(host, Program.PORT, voter.Key.Cookies, election.Id, HomoCrypto.EncryptVector(voter.Value, election.PublicKey));
			log.Info("Voted");

			var state = new Vuln2State
			{
				ElectionId = election.Id.ToString(),
				Voter = voters[0].Key
			};

			Program.ExitWithMessage(ExitCode.OK, null, Convert.ToBase64String(Encoding.UTF8.GetBytes(state.ToJsonString())));
		}

		private static int[][] GenVotes(string flag, Election election)
		{
			var candidateInfos = election.Candidates.ToArray();
			var votes = flag.Select(c =>
			{
				var votePos = candidateInfos.IndexOf(info => info.PublicMessage == c.ToString());
				if(votePos < 0)
					throw new ServiceException(ExitCode.MUMBLE, "Nominated candidates for all flag characters but in resulting election have not for all");
				return Utils.GenVoteVector(candidateInfos.Length, votePos);
			}).ToArray();
			return votes;
		}

		private static User[] RegisterCandidates(string host, User[] users)
		{
			log.Info("Registering candidates...");
			var candidateTasks = users.Select(candidate => new { candidate, task = ElectroClient.RegUserAsync(host, Program.PORT, candidate.Login, candidate.Pass, candidate.PublicMessage, candidate.PrivateMessage) }).ToArray();
			try
			{
				var result = candidateTasks.Select(arg =>
				{
					arg.candidate.Cookies = arg.task.Result;
					return arg.candidate;
				}).ToArray();
				log.InfoFormat("Registered {0} candidates", result.Length);
				return result;
			}
			catch(Exception e)
			{
				throw new ServiceException(ExitCode.DOWN, string.Format("Failed to reg {0} candidates in parallel: {1}", candidateTasks.Length, e));
			}
		}

		private static Election StartElection(string host, User candidate)
		{
			log.Info("Starting election by first candidate...");
			var election = ElectroClient.StartElection(host, Program.PORT, candidate.Cookies, Utils.GenRandomElectionName(), false, nominateTimeInSec, voteTimeInSec);
			if(election == null)
				throw new ServiceException(ExitCode.MUMBLE, "Can't start election - result is NULL");
			log.InfoFormat("Election {0} sarted", election.Id);
			return election;
		}

		private static Election NominateUsers(string host, Election election, User[] candidates)
		{
			log.InfoFormat("Nominating rest {0} candidates for election...", candidates.Length);
			var nominateTasks = candidates.Select(candidate => new { candidate, task = ElectroClient.NominateAsync(host, Program.PORT, candidate.Cookies, election.Id) }).ToArray();
			Election[] elections;
			try
			{
				elections = nominateTasks.Select(arg => arg.task.Result).ToArray();
			}
			catch(Exception e)
			{
				throw new ServiceException(ExitCode.DOWN, string.Format("Failed to nominate {0} candidates in parallel: {1}", nominateTasks.Length, e));
			}

			var electionId = election.Id;
			election = elections.FirstOrDefault(election1 => election1.Candidates.Count >= candidates.Length + 1);
			if(election == null)
				throw new ServiceException(ExitCode.MUMBLE, string.Format("Nominated '{0}' candidates for election '{1}', but got less in result", candidates.Length + 1, electionId));

			log.Info("Candidates nomindated");
			return election;
		}

		private static KeyValuePair<User, int[]>[] RegisterVoters(string host, int[][] votes, User[] candidateUsers)
		{
			var fakeTasks = votes.Take(candidateUsers.Length).Zip(candidateUsers, (vote, voter) => new {vote, voter, task = Task.FromResult(voter.Cookies)});
			var newVotersTasks = votes.Skip(candidateUsers.Length).Select(vote =>
			{
				var voter = UsersManager.GenRandomUser();
				return new  { vote, voter, task = ElectroClient.RegUserAsync(host, Program.PORT, voter.Login, voter.Pass, voter.PublicMessage, voter.PrivateMessage) };
			}).ToArray();

			log.InfoFormat("Registering {0} new voters", newVotersTasks.Length);

			var voterTasks = fakeTasks.Concat(newVotersTasks).ToArray();

			KeyValuePair<User, int[]>[] voters;
			try
			{
				voters = voterTasks.Select(arg => { arg.voter.Cookies = arg.task.Result; return new KeyValuePair<User, int[]>(arg.voter, arg.vote); }).ToArray();
			}
			catch(AggregateException e)
			{
				throw new ServiceException(ExitCode.DOWN, string.Format("Failed to reg {0} voters in parallel: {1}", newVotersTasks.Length, e.Flatten()));
			}

			log.Info("Voters registered");
			return voters;
		}

		public static void ProcessGet(string host, string id, string flag)
		{
			var state = JsonHelper.ParseJson<Vuln2State>(Convert.FromBase64String(id));

			var election = ElectroClient.FindElection(host, Program.PORT, state.Voter.Cookies, state.ElectionId);
			if(election == null || election.Candidates == null)
				throw new ServiceException(ExitCode.MUMBLE, string.Format("Can't find election '{0}' or it has no candidates", id));
			var gotFlag = string.Join("", election.Candidates.WhereNotNull().Select(info => info.PublicMessage ?? ""));
			if(flag != gotFlag)
				throw new ServiceException(ExitCode.CORRUPT, string.Format("Can't find flag. Got '{0}' instead of expected", gotFlag));

			Program.ExitWithMessage(ExitCode.OK, "Flag found! OK");
		}

		private static readonly ILog log = LogManager.GetLogger(typeof(Vuln2Methods));
	}
}
