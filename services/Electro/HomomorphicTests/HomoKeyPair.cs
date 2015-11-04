using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Text;
using System.Threading.Tasks;

namespace HomomorphicTests
{
	class HomoKeyPair
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

	class PublicKey
	{
		public BigInteger[] PK;

		public static PublicKey GenPublicKey(PrivateKey privateKey, int maxNum, int bitsCount = DefaultBitsCount)
		{
			var buff = new BigInteger[DefaultSetSize];

			byte[] rand = new byte[bitsCount / 8];
			Random r = new Random();

			BigInteger rem;
			for(int i = 0; i < buff.Length; i++)
			{
				r.NextBytes(rand);
				buff[i] = (BigInteger.Abs(new BigInteger(rand)) * privateKey.P) + (maxNum * r.Next(10, 100));
			}

			return new PublicKey { PK = buff };
		}

		public const int DefaultBitsCount = 8 * 16;

		public const int DefaultSetSize = 16;
	}

	class PrivateKey
	{
		public BigInteger P;

		public static PrivateKey GenPrivateKey(int maxNum, int bitsCount = DefaultBitsCount)
		{
			var buff = new byte[bitsCount/8];
			while(true)
			{
				new Random().NextBytes(buff);
				var p = new BigInteger(buff);
				if(p % maxNum == 0)
					continue;

				return new PrivateKey { P = p };
			}
		}

		public const int DefaultBitsCount = 8 * 16;
	}
}
