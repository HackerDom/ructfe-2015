using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Serialization;
using System.Text;
using System.Threading.Tasks;

namespace ElectroChecker
{
	[DataContract]
	class Vuln2State
	{
		[DataMember] public string ElectionId { get; set; }
		[DataMember] public User Voter;
	}
}
