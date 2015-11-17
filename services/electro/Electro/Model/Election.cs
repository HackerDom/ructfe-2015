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
	public class Election
	{
		[DataMember(Order = 1)] public Guid Id { get; set; }
		[DataMember(Order = 2)] public string Name { get; set; }

		[DataMember(Order = 3)] private CandidateInfo[] candidates { get; set; }
		[IgnoreDataMember] public List<CandidateInfo> Candidates { get; set; }

		[DataMember(Order = 4)] public bool IsPublic { get; set; }

		[DataMember(Order = 5)] private string nominateTill { get; set; }
		[IgnoreDataMember] public DateTime NominateTill;

		[DataMember(Order = 6)] private string voteTill { get; set; }
		[IgnoreDataMember] public DateTime VoteTill;

		[DataMember(Order = 7)] public PublicKey PublicKey { get; set; }
		[DataMember(Order = 8)] public PrivateKey PrivateKeyForCandidates { get; set; }

		[DataMember(Order = 9)] private Vote[] votes { get; set; }
		[IgnoreDataMember] public List<Vote> Votes { get; set; }
		
		[DataMember(Order = 10)] public BigInteger[] EncryptedResult { get; set; }
		[DataMember(Order = 11)] public int[] DecryptedResult { get; set; }

		[DataMember(Order = 12)] public bool IsNominationFinished  { get { return NominateTill < DateTime.UtcNow; } set {} }
		[DataMember(Order = 13)] public bool IsFinished  { get { return VoteTill < DateTime.UtcNow; } set {} }

		[OnSerializing]
		private void OnSerializing(StreamingContext context)
		{
			if(Candidates != null)
				candidates = Candidates.ToArray();
			if(Votes != null)
				votes = Votes.ToArray();
			nominateTill = NominateTill.ToSortable();
			voteTill = VoteTill.ToSortable();
		}

		[OnDeserialized]
		private void OnDeserialized(StreamingContext context)
		{
			if(candidates != null)
				Candidates = new List<CandidateInfo>(candidates);
			if(votes != null)
				Votes = new List<Vote>(votes);
			NominateTill = DateTimeUtils.TryParseSortable(nominateTill);
			VoteTill = DateTimeUtils.TryParseSortable(voteTill);
		}

		public CandidateInfo FindWinner()
		{
			if(DecryptedResult == null)
				return null;

			int max = int.MinValue;
			CandidateInfo winner = null;

			Candidates
				.Zip(DecryptedResult, (c, v) => new { candidate = c, votesCount = v })
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

		public Election Clone()
		{
			return JsonHelper.ParseJson<Election>(this.ToJsonString());
		}
	}

	[DataContract]
	class ElectionPublicCore
	{
		public static ElectionPublicCore Create(Election election)
		{
			return new ElectionPublicCore
			{
				Id = election.Id,
				Name = election.Name,
				NominateTill = election.NominateTill,
				VoteTill = election.VoteTill,
				Winner = election.FindWinner()
			};
		}

		[DataMember] public Guid Id { get; set; }
		[DataMember] public string Name { get; set; }
		[DataMember] public CandidateInfo Winner { get; set; }

		[DataMember] private string nominateTill { get; set; }
		[IgnoreDataMember] public DateTime NominateTill;

		[DataMember] private string voteTill { get; set; }
		[IgnoreDataMember] public DateTime VoteTill;

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
}
