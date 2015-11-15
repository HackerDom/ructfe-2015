using System;
using System.Runtime.Serialization;

namespace Electro.Model
{
	[DataContract]
	class User
	{
		[DataMember] public Guid Id { get; set; }
		[DataMember] public string Login { get; set; }
		[DataMember] public string PublicMessage { get; set; }

		[DataMember] public string PasswordHash { get; set; }
		[DataMember] public string PrivateNotes { get; set; }
	}

	[DataContract]
	class CandidateInfo
	{
		[DataMember] public Guid Id { get; set; }
		[DataMember] public string Name { get; set; }
		[DataMember] public string PublicMessage { get; set; }

		public static CandidateInfo Create(User user)
		{
			return new CandidateInfo
			{
				Id = user.Id,
				Name = user.Login,
				PublicMessage = user.PublicMessage
			};
		}
	}
}
