using System;
using System.Linq;
using System.Numerics;
using System.Runtime.Serialization;

namespace Electro.Crypto
{
	class Singleton
	{
		public static Random Random = new Random();
	}

	public class HomoKeyPair
	{
		public PublicKey PublicKey { get; set; }
		public PrivateKey PrivateKey { get; set; }

		public static HomoKeyPair GenKeyPair(int maxNum)
		{
			var privateKey = PrivateKey.GenPrivateKey(maxNum);
			return new HomoKeyPair
			{
				PrivateKey = privateKey,
				PublicKey = PublicKey.GenPublicKey(privateKey, maxNum)
			};
		}
	}

	[DataContract]
	public class PublicKey
	{
		[DataMember] public string[] keyParts;
		[IgnoreDataMember] public BigInteger[] KeyParts;

		[OnSerializing]
		private void OnSerializing(StreamingContext context)
		{
			if(KeyParts != null)
				keyParts = KeyParts.Select(b => b.ToString()).ToArray();
		}

		[OnDeserialized]
		private void OnDeserialized(StreamingContext context)
		{
			bool failed = false;
			if(keyParts != null)
			{
				var result = keyParts.Select(s =>
				{
					BigInteger b;
					if(!BigInteger.TryParse(s, out b))
						failed = true;
					return b;
				}).ToArray();
				if(!failed)
					KeyParts = result;
			}
		}

		public static PublicKey GenPublicKey(PrivateKey privateKey, int bitsCount = DefaultBitsCount)
		{
			var buff = new BigInteger[DefaultSetSize];

			byte[] rand = new byte[bitsCount / 8];
			for(int i = 0; i < buff.Length; i++)
			{
				Singleton.Random.NextBytes(rand);
				buff[i] = (BigInteger.Abs(new BigInteger(rand)) * privateKey.Key) + (privateKey.MaxNum * Singleton.Random.Next(10, 100));
			}

			return new PublicKey { KeyParts = buff };
		}

		public const int DefaultBitsCount = 8 * 16;

		public const int DefaultSetSize = 16;
	}

	[DataContract]
	public class PrivateKey
	{
		[DataMember] public string key { get; set; }
		[IgnoreDataMember] public BigInteger Key { get; set; }

		[DataMember] public int MaxNum { get; set; }

		[OnSerializing]
		private void OnSerializing(StreamingContext context)
		{
			key = Key.ToString();
		}

		[OnDeserialized]
		private void OnDeserialized(StreamingContext context)
		{
			BigInteger b;
			if(BigInteger.TryParse(key, out b))
				Key = b;
		}

		public static PrivateKey GenPrivateKey(int maxNum, int bitsCount = DefaultBitsCount)
		{
			var buff = new byte[bitsCount/8];
			while(true)
			{
				Singleton.Random.NextBytes(buff);
				var p = BigInteger.Abs(new BigInteger(buff));
				return new PrivateKey { Key = p, MaxNum = maxNum};
			}
		}

		public const int DefaultBitsCount = 8 * 16;
	}
}
