using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using Electro.Crypto;
using Electro.Model;
using Electro.Utils;

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
			e.ForEach(election => elections[election.Id] = election);
			k.ForEach(kvp => electionPrivateKeys[kvp.Key] = kvp.Value);
		}

		public Guid StartElection(string electionName, User firstCandidate, bool isPublic, DateTime nominateTill, DateTime till)
		{
			var homoKeyPair = HomoKeyPair.GenKeyPair(MaxVotes);
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

			statePersister.SaveElection(election);
			statePersister.SaveKey(election.Id, homoKeyPair.PrivateKey);

			electionPrivateKeys[election.Id] = homoKeyPair.PrivateKey;
			elections[election.Id] = election;

			return election.Id;
		}

		public Election NominateCandidate(Guid electionId, User user)
		{
			Election election;
			if(!elections.TryGetValue(electionId, out election))
				return null;

			lock (election)
			{
				if(election.IsNominationFinished)
					return null;

				if(election.Candidates.Any(info => info.Id == user.Id))
					return null;

				election.Candidates.Add(CandidateInfo.Create(user));

				statePersister.SaveElection(election);
				return election;
			}
		}

		public bool Vote(Guid electionId, User user, BigInteger[] voteArray)
		{
			Election election;
			if(!elections.TryGetValue(electionId, out election))
				return false;

			lock(election)
			{
				if(!election.IsNominationFinished || election.IsFinished)
					return false;

				if(election.Votes.Count == MaxVotes)
					return false;

				var vote = new Vote { UserId = user.Id, EncryptedVector = voteArray };
				var result = election.EncryptedResult ?? new BigInteger[vote.EncryptedVector.Length];
				election.EncryptedResult = TryMerge(result, vote);

				election.Votes.Add(vote);

				statePersister.SaveElection(election);
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
			if(!elections.TryGetValue(electionId, out election))
				return null;
			TryDecryptElectionResultIfFinished(election);

			if(election.Candidates.Any(info => info.Id == user.Id))
			{
				lock(election)
				{
					election = election.Clone();
				}

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
					} );
			}

			return election;
		}

		public IEnumerable<Election> GetUnfinishedPublicElections()
		{
			return elections.Where(pair => !pair.Value.IsFinished && pair.Value.IsPublic).Select(pair => pair.Value);
		}

		public IEnumerable<Election> GetFinishedElections()
		{
			return elections.Where(pair => pair.Value.IsFinished).With(pair => TryDecryptElectionResultIfFinished(pair.Value)).Select(pair => pair.Value);
		}

		public bool TryDecryptElectionResultIfFinished(Election election)
		{
			if(!election.IsFinished)
				return false;

			PrivateKey privateKey;
			if(!electionPrivateKeys.TryGetValue(election.Id, out privateKey))
				return false;

			if(election.EncryptedResult != null)
				election.DecryptedResult = election.EncryptedResult.Select(voteElement => HomoCrypto.Decrypt(voteElement, privateKey)).ToArray();

			return true;
		}

		private const int MaxVotes = 1024;

		private ConcurrentDictionary<Guid, PrivateKey> electionPrivateKeys = new ConcurrentDictionary<Guid, PrivateKey>();
		private ConcurrentDictionary<Guid, Election> elections = new ConcurrentDictionary<Guid, Election>();
	}
}
