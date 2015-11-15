using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Serialization;
using System.Text;
using System.Threading.Tasks;
using Electro.Utils;

namespace Electro.Model
{
	[DataContract]
	class Election
	{
		[DataMember(Order = 1)] public Guid Id { get; set; }
		[DataMember(Order = 2)] public string Name { get; set; }
		[DataMember(Order = 3)] public Dictionary<Guid, UserPublic> Candidates { get; set; }
		[DataMember(Order = 4)] public bool IsPublic { get; set; }

		[DataMember(Order = 5)] private string till { get; set; }
		[IgnoreDataMember] public DateTime Till { get { return DateTimeUtils.TryParseSortable(till); } set {till = value.ToSortable();} }

		[DataMember(Order = 6)] public Dictionary<Guid, Vote> Votes { get; set; }

		//TODO add HasStartedAttribute and check it when voting and registering candidates
		[IgnoreDataMember] public bool IsFinished  { get { return Till < DateTime.UtcNow; } }
	}

	[DataContract]
	class ElectionPulicCore
	{
		public static ElectionPulicCore Create(Election election)
		{
			return new ElectionPulicCore {Id = election.Id, Name = election.Name, Till = election.Till};
		}

		[DataMember] public Guid Id { get; set; }
		[DataMember] public string Name { get; set; }

		[DataMember] private string till { get; set; }
		[IgnoreDataMember] public DateTime Till { get { return DateTimeUtils.TryParseSortable(till); } set {till = value.ToSortable();} }
	}
}
