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
		public Election StartElection(string electionName, User firstCandidate, bool isPublic, DateTime nominateTill, DateTime till, out PrivateKey privateKey)
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

			electionPrivateKeys[election.Id] = privateKey = homoKeyPair.PrivateKey;
			elections[election.Id] = election;

			return election;
		}

		public PrivateKey NominateCandidate(Guid electionId, User user)
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
				return electionPrivateKeys[electionId];
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
			}

			return true;
		}

		public BigInteger[] TryMerge(BigInteger[] voteResults, Vote v)
		{
			if(voteResults == null || v == null || v.EncryptedVector == null || voteResults.Length != v.EncryptedVector.Length)
				return null;

			return Enumerable.Range(0, voteResults.Length).Select(i => voteResults[i] + v.EncryptedVector[i]).ToArray();
		}

		public Election FindElection(Guid electionId)
		{
			Election election;
			if(!elections.TryGetValue(electionId, out election))
				return null;
			TryDecryptElectionResult(election);
			return election;
		}

		public IEnumerable<Election> GetUnfinishedPublicElections()
		{
			return elections.Where(pair => !pair.Value.IsFinished && pair.Value.IsPublic).Select(pair => pair.Value);
		}

		public IEnumerable<Election> GetFinishedElections()
		{
			return elections.Where(pair => pair.Value.IsFinished).With(pair => TryDecryptElectionResult(pair.Value)).Select(pair => pair.Value);
		}

		public bool TryDecryptElectionResult(Election election)
		{
			if(!election.IsFinished)
				return false;

			PrivateKey privateKey;
			if(!electionPrivateKeys.TryGetValue(election.Id, out privateKey))
				return false;

			election.DecryptedResult = election.EncryptedResult.Select(voteElement => HomoCrypto.Decrypt(voteElement, privateKey)).ToArray();
			return true;
		}

		private const int MaxVotes = 1024;

		private ConcurrentDictionary<Guid, PrivateKey> electionPrivateKeys = new ConcurrentDictionary<Guid, PrivateKey>();
		private ConcurrentDictionary<Guid, Election> elections = new ConcurrentDictionary<Guid, Election>();
	}
}
