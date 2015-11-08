using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Text;
using System.Threading.Tasks;

namespace HomomorphicTests
{
	class Singleton
	{
		public static Random Random = new Random();
	}

	public class HomoKeyPair
	{
		public PublicKey publicKey;
		public PrivateKey privateKey;
		public int MaxNum;

		public static HomoKeyPair GenKeyPair(int maxNum)
		{
			var privateKey = PrivateKey.GenPrivateKey(maxNum);
			return new HomoKeyPair
			{
				MaxNum = maxNum,
				privateKey = privateKey,
				publicKey = PublicKey.GenPublicKey(privateKey, maxNum)
			};
		}
	}


	public class PublicKey
	{
		public BigInteger[] PK;

		public static PublicKey GenPublicKey(PrivateKey privateKey, int maxNum, int bitsCount = DefaultBitsCount)
		{
			var buff = new BigInteger[DefaultSetSize];

			byte[] rand = new byte[bitsCount / 8];
			for(int i = 0; i < buff.Length; i++)
			{
				Singleton.Random.NextBytes(rand);
				buff[i] = (BigInteger.Abs(new BigInteger(rand)) * privateKey.P) + (maxNum * Singleton.Random.Next(10, 100));
			}

			return new PublicKey { PK = buff };
		}

		public const int DefaultBitsCount = 8 * 16;

		public const int DefaultSetSize = 16;
	}


	public class PrivateKey
	{
		public BigInteger P;

		public static PrivateKey GenPrivateKey(int maxNum, int bitsCount = DefaultBitsCount)
		{
			var buff = new byte[bitsCount/8];
			while(true)
			{
				Singleton.Random.NextBytes(buff);
				var p = BigInteger.Abs(new BigInteger(buff));
				return new PrivateKey { P = p };
			}
		}

		public const int DefaultBitsCount = 8 * 16;
	}
}
