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
		public bool AddUser(User user)
		{
			return users.TryAdd(user.Id, user);
		}

		public Election StartElection(string name, User firstCandidate, bool isPublic)
		{
			var election = new Election { Id = Guid.NewGuid(), Name = name, Candidates = new Dictionary<Guid, User> { {firstCandidate.Id, firstCandidate } }, IsPublic = isPublic};
			elections[election.Id] = election;
			return election;
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

		private ConcurrentDictionary<Guid, User> users;
		private ConcurrentDictionary<Guid, Election> elections;
	}
}
