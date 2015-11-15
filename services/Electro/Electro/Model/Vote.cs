using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Numerics;
using System.Runtime.Serialization;
using System.Text;
using System.Threading.Tasks;
using Electro.Crypto;

namespace Electro.Model
{
	[DataContract]
	class Vote
	{
		[DataMember(EmitDefaultValue = false)] public Guid UserId { get; set; }
		[DataMember] public BigInteger[] EncryptedVector { get; set; }
	}

	static class VoteExtensions
	{
		public static int[] DecryptVote(this Vote vote, PrivateKey key)
		{
			if(vote == null || key == null || vote.EncryptedVector == null)
				throw new Exception("Can't decrypt vote. Null key or vote");
			return vote.EncryptedVector.Select(arg => HomoCrypto.Decrypt(arg, key)).ToArray();
		}

		public static Vote EncryptVote(int[] vector, Guid usetId, PublicKey key)
		{
			if(vector == null || key == null)
				throw new Exception("Can't encrypt vote. Null key or vector");
			return new Vote {UserId = usetId, EncryptedVector = vector.Select(arg => HomoCrypto.Encrypt(arg, key)).ToArray()};
		}
    }
}
