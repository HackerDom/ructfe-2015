using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using Electro.Crypto;
using Electro.Model;
using Electro.Utils;
using log4net;

namespace Electro
{
	class ElectroController
	{
		private readonly AuthController authController;
		private readonly StatePersister statePersister;

		public ElectroController(IEnumerable<Election> elections, IEnumerable<KeyValuePair<Guid, PrivateKey>> keys, AuthController authController, StatePersister statePersister)
		{
			this.authController = authController;
			this.statePersister = statePersister;

			LoadState(elections, keys);
		}

		private void LoadState(IEnumerable<Election> e, IEnumerable<KeyValuePair<Guid, PrivateKey>> k)
		{
			log.InfoFormat("Loading elections state");
			lock (electionsList)
			{
				int lines = 0;
				e.ForEach(election =>
				{
					if(++lines % 100 == 0)
						log.InfoFormat("Loaded {0} lines of election state", lines);
					electionsList.AddFirst(election);
					electionsDict[election.Id] = election;
				});
			}
			log.InfoFormat("Loaded elections state. Now have {0} elections", electionsDict.Count);
			k.ForEach(kvp => electionPrivateKeys[kvp.Key] = kvp.Value);
			log.InfoFormat("Loaded  keys state. Now have {0} keys", electionPrivateKeys.Count);
		}

		public Guid StartElection(string electionName, User firstCandidate, bool isPublic, DateTime nominateTill, DateTime till)
		{
			var homoKeyPair = HomoKeyPair.GenKeyPair(MaxVotesPerElection);
			var election = new Election
			{
				Id = Guid.NewGuid(),
				Name = electionName,
				NominateTill = nominateTill,
				VoteTill = till,
				PublicKey = homoKeyPair.PublicKey,
				Votes = new List<Vote>(),
				Candidates = new List<CandidateInfo> { CandidateInfo.Create(firstCandidate) },
				IsPublic = isPublic
			};

			statePersister.SaveKey(election.Id, homoKeyPair.PrivateKey);

			lock (electionsList)
			{
				electionPrivateKeys[election.Id] = homoKeyPair.PrivateKey;
				electionsDict[election.Id] = election;

				electionsList.AddFirst(election);
				while(electionsList.Count > MaxElections)
				{
					var node = electionsList.Last;
					Election dummy;
					electionsDict.TryRemove(node.Value.Id, out dummy);
					electionsList.RemoveLast();
				}
			}

			return election.Id;
		}

		public Election NominateCandidate(Guid electionId, User user)
		{
			Election election;
			if(!electionsDict.TryGetValue(electionId, out election))
				return null;

			lock (election)
			{
				if(election.IsNominationFinished)
					return null;

				if(election.Candidates.Any(info => info.Id == user.Id))
					return null;

				election.Candidates.Add(CandidateInfo.Create(user));

				var clone = election.Clone();
				PrivateKey privateKey;
				if(electionPrivateKeys.TryGetValue(clone.Id, out privateKey))
					clone.PrivateKeyForCandidates = privateKey;

				return clone;
			}
		}

		public bool Vote(Guid electionId, User user, BigInteger[] voteArray)
		{
			Election election;
			if(!electionsDict.TryGetValue(electionId, out election))
				return false;

			lock(election)
			{
				if(!election.IsNominationFinished || election.IsFinished)
					return false;

				if(election.Votes.Count == MaxVotesPerElection)
					return false;

				if(election.Candidates.Count != voteArray.Length)
					return false;

				if(election.Votes.Any(v => v.UserId == user.Id))
					return false;

				var vote = new Vote { UserId = user.Id, EncryptedVector = voteArray };
				var result = election.EncryptedResult ?? new BigInteger[vote.EncryptedVector.Length];
				election.EncryptedResult = TryMerge(result, vote);

				election.Votes.Add(vote);
			}

			return true;
		}

		private BigInteger[] TryMerge(BigInteger[] voteResults, Vote v)
		{
			if(voteResults == null || v == null || v.EncryptedVector == null || voteResults.Length != v.EncryptedVector.Length)
				return null;

			return Enumerable.Range(0, voteResults.Length).Select(i => voteResults[i] + v.EncryptedVector[i]).ToArray();
		}

		public Election FindElectionForUser(Guid electionId, User user)
		{
			Election election;
			if(!electionsDict.TryGetValue(electionId, out election))
				return null;
			TryDecryptElectionResultIfFinished(election);

			if(election.Candidates.Any(info => info.Id == user.Id))
			{
				lock(election)
				{
					election = election.Clone();
				}

				var candidate = election.Candidates.FirstOrDefault(info => info.Id == user.Id);
				if(candidate != null)
					candidate.IsMe = true;

				PrivateKey privateKey;
				if(electionPrivateKeys.TryGetValue(election.Id, out privateKey))
					election.PrivateKeyForCandidates = privateKey;

				var winner = election.FindWinner();
				if(winner != null && winner.Id == user.Id)
					election.Candidates.ForEach(info =>
						{
							var u = authController.FindUserAuthorized(info.Name);
							if(u != null)
								info.PrivateNotesForWinner = u.PrivateNotes;
						}
					);
			}

			return election;
		}

		public IEnumerable<Election> GetUnfinishedPublicElections(int top = int.MaxValue)
		{
			lock(electionsList)
			{
				return electionsList.Where(election => !election.IsFinished && election.IsPublic).Select(election => election).Take(top).ToArray();
			}
			
		}

		public IEnumerable<Election> GetFinishedElections(int top = int.MaxValue)
		{
			lock(electionsList)
			{
				return electionsList.Where(election => election.IsFinished ).Select(election => election).Take(top).With(election => TryDecryptElectionResultIfFinished(election)).ToArray();
			}
		}

		public bool TryDecryptElectionResultIfFinished(Election election)
		{
			if(!election.IsFinished)
				return false;

			PrivateKey privateKey;
			if(!electionPrivateKeys.TryGetValue(election.Id, out privateKey))
				return false;

			election.DecryptedResult = (election.EncryptedResult ?? Enumerable.Repeat(BigInteger.Zero, election.Candidates.Count)).Select(voteElement => HomoCrypto.Decrypt(voteElement, privateKey)).ToArray();

			return true;
		}

		public IEnumerable<Election> DumpElections()
		{
			lock(electionsList)
			{
				return electionsList.ToArray();
			}
		}

		private const int MaxElections = 1000;
		private const int MaxVotesPerElection = 243;

		private ConcurrentDictionary<Guid, PrivateKey> electionPrivateKeys = new ConcurrentDictionary<Guid, PrivateKey>();
		private ConcurrentDictionary<Guid, Election> electionsDict= new ConcurrentDictionary<Guid, Election>();
		private LinkedList<Election> electionsList = new LinkedList<Election>();

		private static readonly ILog log = LogManager.GetLogger(typeof(ElectroController));
	}
}
