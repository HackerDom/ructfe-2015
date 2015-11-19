using System;
using System.Runtime.Serialization;

namespace Electro.Model
{
	[DataContract]
	public class CandidateInfo
	{
		[DataMember] public Guid Id { get; set; }
		[DataMember] public string Name { get; set; }
		[DataMember] public string PublicMessage { get; set; }
		[DataMember] public string PrivateNotesForWinner { get; set; }
		[DataMember] public bool IsMe { get; set; }

		public static CandidateInfo Create(User user)
		{
			return new CandidateInfo
			{
				Id = user.Id,
				Name = user.Login,
				PublicMessage = user.PublicMessage,
			};
		}
	}
}