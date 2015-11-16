using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ElectroChecker
{
	static class Utils
	{
		public static int FindWinner(int[] votes)
		{
			int num = -1;
			int max = -1;
			for(int i = 0; i < votes.Length; i++)
			{
				if(votes[i] > max)
				{
					max = votes[i];
					num = i;
				}
			}
			return num;
		}

		public static int[] SumVoteVectors(List<int[]> votes)
		{
			var result = Enumerable.Repeat(0, votes[0].Length).ToArray();
			foreach(var second in votes)
				result.AddVoteVector(second);
			return result;
		}

		public static void AddVoteVector(this int[] first, int[] second)
		{
			for(int i = 0; i < first.Length; i++)
				first[i] += second[i];
		}

		public static int[] GenVoteVector(int count, int winner)
		{
			var result = Enumerable.Repeat(0, count).ToArray();
			result[winner] = 1;
			return result;
		}

		public static IEnumerable<int[]> GenRandomVoteVectors(int vectorSize, int minCount, int maxCount)
		{
			var count = random.Next(minCount, maxCount + 1);
			return Enumerable.Range(0, count).Select(i => GenRandomVoteVector(vectorSize));
		}

		public static int[] GenRandomVoteVector(int vectorSize)
		{
			var result = new int[vectorSize];
			result[random.Next(vectorSize)] = 1;
			return result;
		}

		public static string GenRandomAlphaNumeric(int minLen = 6, int plusRandomLen = 2)
		{
			const string chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
			var len = minLen + random.Next(plusRandomLen + 1);
			return string.Join("", Enumerable.Range(0, len).Select(i => chars[random.Next(0, chars.Length)]));
		}

		static Random random = new Random();
	}
}
