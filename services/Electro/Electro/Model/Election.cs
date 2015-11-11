using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Serialization;
using System.Text;
using System.Threading.Tasks;

namespace Electro.Model
{
	[DataContract]
	class Election
	{
		[DataMember] public Guid Id { get; set; }
		[DataMember] public string Name { get; set; }
		[DataMember] public Dictionary<Guid, User> Candidates { get; set; }
		[DataMember] public bool IsPublic { get; set; }
		[DataMember] public bool IsFinished { get; set; }

		[DataMember] public Dictionary<Guid, Vote> Votes { get; set; }
	}
}
