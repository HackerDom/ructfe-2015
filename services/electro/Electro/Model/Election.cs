using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Runtime.Serialization;
using Electro.Crypto;
using Electro.Utils;

namespace Electro.Model
{
	[DataContract]
	class Election
	{
		[DataMember(Order = 1)] public Guid Id { get; set; }
		[DataMember(Order = 2)] public string Name { get; set; }
		[DataMember(Order = 3)] public List<CandidateInfo> Candidates { get; set; }
		[DataMember(Order = 4)] public bool IsPublic { get; set; }

		[DataMember(Order = 5)] private string nominateTill { get; set; }
		[IgnoreDataMember] public DateTime NominateTill;

		[DataMember(Order = 6)] private string voteTill { get; set; }
		[IgnoreDataMember] public DateTime VoteTill;

		[DataMember(Order = 7)] public PublicKey PublicKey { get; set; }
		[DataMember(Order = 8)] public List<Vote> Votes { get; set; }
		
		[DataMember(Order = 9)] public BigInteger[] EncryptedResult { get; set; }
		[DataMember(Order = 10)] public int[] DecryptedResult { get; set; }

		[IgnoreDataMember] public bool IsNominationFinished  { get { return NominateTill < DateTime.UtcNow; } }
		[IgnoreDataMember] public bool IsFinished  { get { return VoteTill < DateTime.UtcNow; } }

		[IgnoreDataMember]
		public CandidateInfo Winner
		{
			get
			{
				if(DecryptedResult == null)
					return null;

				int max = int.MinValue;
				CandidateInfo winner = null;

				Candidates
					.Zip(DecryptedResult, (c, v) => new {candidate = c, votesCount = v})
					.ForEach(arg =>
					{
						if(arg.votesCount > max)
						{
							max = arg.votesCount;
							winner = arg.candidate;
						}
					});
				return winner;
			}
		}

		[OnSerializing]
		private void OnSerializing(StreamingContext context)
		{
			nominateTill = NominateTill.ToSortable();
			voteTill = VoteTill.ToSortable();
		}

		[OnDeserialized]
		private void OnDeserialized(StreamingContext context)
		{
			NominateTill = DateTimeUtils.TryParseSortable(nominateTill);
			VoteTill = DateTimeUtils.TryParseSortable(voteTill);
		}
	}

	[DataContract]
	class ElectionPulicCore
	{
		public static ElectionPulicCore Create(Election election)
		{
			return new ElectionPulicCore
			{
				Id = election.Id,
				Name = election.Name,
				Till = election.VoteTill,
				Winner = election.Winner
			};
		}

		[DataMember] public Guid Id { get; set; }
		[DataMember] public string Name { get; set; }
		[DataMember] public CandidateInfo Winner { get; set; }

		[DataMember] private string till { get; set; }
		[IgnoreDataMember] public DateTime Till { get { return DateTimeUtils.TryParseSortable(till); } set {till = value.ToSortable();} }
	}
}
