using System;
using System.Runtime.Serialization;
using Electro.Model;
using Electro.Utils;

namespace ElectroChecker
{
	[DataContract]
	class Vuln1State
	{
		[DataMember] private string electionStartDate;
		[IgnoreDataMember] public DateTime ElectionStartDate;

		[DataMember] public int NominateTimeInSec { get; set; }
		[DataMember] public int VoteTimeInSec { get; set; }
		[DataMember] public string ElectionId;
		[DataMember] public User[] Candidates { get; set; }

		[OnSerializing]
		private void OnSerializing(StreamingContext context)
		{
			electionStartDate = ElectionStartDate.ToSortable();
		}

		[OnDeserialized]
		private void OnDeserialized(StreamingContext context)
		{
			ElectionStartDate = DateTimeUtils.TryParseSortable(electionStartDate);
		}
	}
}