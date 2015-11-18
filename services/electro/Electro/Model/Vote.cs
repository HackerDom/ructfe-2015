using System;
using System.Linq;
using System.Numerics;
using System.Runtime.Serialization;
using Electro.Crypto;

namespace Electro.Model
{
	[DataContract]
	public class Vote
	{
		[DataMember(EmitDefaultValue = false)] public Guid UserId { get; set; }

		[DataMember] public string[] encryptedVector { get; set; }
		[IgnoreDataMember] public BigInteger[] EncryptedVector { get; set; }

		[OnSerializing]
		private void OnSerializing(StreamingContext context)
		{
			if(EncryptedVector != null)
				encryptedVector = EncryptedVector.Select(b => b.ToString()).ToArray();
		}

		[OnDeserialized]
		private void OnDeserialized(StreamingContext context)
		{
			bool failed = false;
			if(encryptedVector != null)
			{
				var result = encryptedVector.Select(s =>
				{
					BigInteger b;
					if(!BigInteger.TryParse(s, out b))
						failed = true;
					return b;
				}).ToArray();
				if(!failed)
					EncryptedVector = result;
			}
		}
	}

	public static class VoteExtensions
	{
		public static int[] DecryptVote(this Vote vote, PrivateKey key)
		{
			if(vote == null || key == null || vote.EncryptedVector == null)
				throw new Exception("Can't decrypt vote. Null key or vote");
			return vote.EncryptedVector.Select(arg => HomoCrypto.Decrypt(arg, key)).ToArray();
		}
    }
}
