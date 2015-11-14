using System;
using System.Runtime.Serialization;

namespace Electro.Model
{
	[DataContract]
	class User
	{
		[DataMember] public Guid Id { get; set; }
		[DataMember] public string Login { get; set; }
		[DataMember] public string Hash { get; set; }

		[DataMember] public string PublicMessage { get; set; }
		[DataMember] public string PrivateNotes { get; set; }
	}
}
