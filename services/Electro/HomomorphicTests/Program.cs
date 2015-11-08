using System;
using System.Collections.Generic;
using System.Diagnostics;
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
			int maxNum = 100;
			var nums = new []{4, 8, 15, 16, 23};

			const int testsCount = 100 * 1000;
			var sw = Stopwatch.StartNew();
			for(int i = 0; i < testsCount; i++)
			{
				int testResult = 0;
				BigInteger encResult = 0;

				var homoKeyPair = HomoKeyPair.GenKeyPair(maxNum);

				foreach(var num in nums)
				{
					testResult += num;
					encResult += Encrypt(num, homoKeyPair.publicKey);
				}

				var decryptedResult = Decrypt(encResult, homoKeyPair.privateKey, maxNum);
				if(testResult != decryptedResult)
				{
					Console.WriteLine("Failed: expected {testResult} got {decryptedResult}");
					Environment.Exit(1);
				}
			}
			sw.Stop();
			Console.WriteLine($"Passed! Done {testsCount} tests in {sw.Elapsed}");
		}

		private static BigInteger Encrypt(int m, PublicKey publicKey)
		{
			BigInteger b = 0;
			var r = new Random();
			for(int i = 0; i < publicKey.PK.Length; i++)
			{
				if(r.Next(2) == 1)
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
