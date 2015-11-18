using System.Runtime.Serialization;
using Electro.Crypto;

namespace ElectroChecker
{
	[DataContract]
	class Vuln2State
	{
		[DataMember] public string ElectionId { get; set; }
		[DataMember] public User Voter;
		[DataMember] public PrivateKey PrivateKey;
	}
}
