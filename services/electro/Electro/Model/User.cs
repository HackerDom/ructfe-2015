using System;
using System.Runtime.Serialization;

namespace Electro.Model
{
	[DataContract]
	public class User
	{
		[DataMember] public Guid Id { get; set; }
		[DataMember] public string Login { get; set; }
		[DataMember] public string PublicMessage { get; set; }

		[DataMember] public string PrivateNotes { get; set; }

		[DataMember] public string PasswordHash { get; set; }
	}
}
