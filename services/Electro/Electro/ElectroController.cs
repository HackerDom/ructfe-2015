using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Remoting.Metadata.W3cXsd2001;
using System.Text;
using System.Threading.Tasks;
using Electro.Model;

namespace Electro
{
	class ElectroController
	{
		public Election StartElection(string electionName, User firstCandidate, bool isPublic, DateTime till)
		{
			var election = new Election { Id = Guid.NewGuid(), Name = electionName, Till = till, Candidates = new Dictionary<Guid, UserPublic> { {firstCandidate.Id, UserPublic.Convert(firstCandidate) } }, IsPublic = isPublic};
			elections[election.Id] = election;
			return election;
		}

		public bool RegisterCandidate(Guid electionId, User user)
		{
			Election election;
			if(!elections.TryGetValue(electionId, out election))
				return false;

			lock (election)
			{
				if(election.IsFinished)
					return false;

				if(election.Candidates.ContainsKey(user.Id))
					return false;

				election.Candidates[user.Id] = UserPublic.Convert(user);
				return true;
			}
		}


		public bool Vote(Guid electionId, User user, Vote vote)
		{
			Election election;
			if(!elections.TryGetValue(electionId, out election))
				return false;

			lock(election)
			{
				if(election.IsFinished)
					return false;

				election.Votes[user.Id] = vote;
			}

			return true;
		}

		public Election FindElection(Guid electionId)
		{
			Election election;
			return elections.TryGetValue(electionId, out election) ? election : null;
		}

		public IEnumerable<Election> GetUnfinishedPublicElections()
		{
			return elections.Where(pair => !pair.Value.IsFinished && pair.Value.IsPublic).Select(pair => pair.Value);
		}

		public IEnumerable<Election> GetFinishedElections()
		{
			return elections.Where(pair => pair.Value.IsFinished).Select(pair => pair.Value);
		}

		public IEnumerable<Election> DumpAllElections()
		{
			return elections.Select(pair => pair.Value);
		}

		private ConcurrentDictionary<Guid, Election> elections = new ConcurrentDictionary<Guid, Election>();
	}
}
