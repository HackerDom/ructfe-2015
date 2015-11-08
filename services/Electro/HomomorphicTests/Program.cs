using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace HomomorphicTests
{
	class Program
	{
		static void Main(string[] args)
		{
			int maxNum = 128;
			var nums = new []{0, 0, 1, 0, 0};

			const int testsCount = 10 * 1000;
			var sw = Stopwatch.StartNew();
			for(int i = 0; i < testsCount; i++)
			{
				int testResult = 0;
				BigInteger encResult = 0;

				var homoKeyPair = HomoKeyPair.GenKeyPair(maxNum);

				foreach(var num in nums)
				{
					testResult += num;
					var c = Encrypt(num, homoKeyPair.publicKey);
					Console.WriteLine($"num {num} c {c}");
					encResult += c;
				}
				Console.WriteLine();
				var decryptedResult = Decrypt(encResult, homoKeyPair.privateKey, maxNum);
				
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
			for(int i = 0; i < publicKey.PK.Length; i++)
			{
				byte[] bb = new byte[1];
				r.GetBytes(bb);
				var random = bb[0]%2;
				Console.Write(random);
				if(i == 0 || random == 1)
					b = b + publicKey.PK[i];
			}
			Console.WriteLine();
			return b + m;
		}

		private static BigInteger Decrypt(BigInteger c, PrivateKey privateKey, int maxNum)
		{
			var m = c % privateKey.P;
			return m % maxNum;
		}
	}
}
