using System;
using System.Numerics;

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

	public class PublicKey
	{
		public BigInteger[] KeyParts;

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

	public class PrivateKey
	{
		public BigInteger Key { get; set; }
		public int MaxNum { get; set; }

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
