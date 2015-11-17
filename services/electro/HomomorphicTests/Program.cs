using System;
using System.Diagnostics;
using System.Numerics;
using System.Security.Cryptography;
using Electro.Crypto;

namespace HomomorphicTests
{
	static class Program
	{
		static void Main(string[] args)
		{
			int maxNum = 81;
			var nums = new []{0, 1, 2};

			const int testsCount = 10;
			var sw = Stopwatch.StartNew();
			for(int i = 0; i < testsCount; i++)
			{
				int testResult = 0;
				BigInteger encResult = 0;

				var homoKeyPair = HomoKeyPair.GenKeyPair(maxNum);

				foreach(var num in nums)
				{
					testResult += num;
					var c = Encrypt(num, homoKeyPair.PublicKey);
					Console.WriteLine($"num {num} c {c}");
					encResult += c;
				}
				Console.WriteLine();
				var decryptedResult = Decrypt(encResult, homoKeyPair.PrivateKey);
				
				if(testResult != decryptedResult)
				{
					Console.WriteLine($"Failed: expected {testResult} got {decryptedResult}");
					Environment.Exit(1);
				}
			}
			sw.Stop();
			Console.WriteLine($"Passed! Done {testsCount} tests in {sw.Elapsed}");
		}

		private static BigInteger Encrypt(int m, PublicKey publicKey)
		{
			BigInteger b = 0;
			var r = RandomNumberGenerator.Create();
			for(int i = 0; i < publicKey.KeyParts.Length; i++)
			{
				byte[] bb = new byte[1];
				r.GetBytes(bb);
				var random = bb[0]%2;
				Console.Write(random);
				if(i == 0 || random == 1)
					b = b + publicKey.KeyParts[i];
			}
			Console.WriteLine();
			return b + m;
		}

		private static BigInteger Decrypt(BigInteger c, PrivateKey privateKey)
		{
			var m = c % privateKey.Key;
			return m % privateKey.MaxNum;
		}
	}
}
