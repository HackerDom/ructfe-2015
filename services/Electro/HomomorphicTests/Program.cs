using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Text;
using System.Threading.Tasks;

namespace HomomorphicTests
{
	class Program
	{
		static void Main(string[] args)
		{
			int maxNum = 67;
			var nums = new []{4, 8, 15, 16, 23};

			int testResult = 0;
			BigInteger encResult = 0;

			var homoKeyPair = HomoKeyPair.GenKeyPair(maxNum);

			foreach(var num in nums)
			{
				testResult += num;
				encResult += Encrypt(num, homoKeyPair.publicKey);
			}

			var decryptedResult = Decrypt(encResult, homoKeyPair.privateKey, maxNum);
			Console.WriteLine(testResult == decryptedResult ? "Passed" : $"Failed: expected {testResult} got {decryptedResult}");
		}

		private static BigInteger Encrypt(int m, PublicKey publicKey)
		{
			var random = new Random();

			BigInteger b = 0;
			for(int i = 0; i < publicKey.PK.Length; i++)
			{
				if(random.Next(2) == 1)
					b = b + publicKey.PK[i];
			}
			return b + m;
		}

		private static BigInteger Decrypt(BigInteger c, PrivateKey privateKey, int maxNum)
		{
			var m = c % privateKey.P;
			return m % maxNum;
		}
	}
}
