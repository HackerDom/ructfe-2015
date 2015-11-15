using System;
using System.IO;

namespace ElectroChecker
{
	class FullNames
	{
		static FullNames()
		{
			names = File.ReadAllLines(namesPath);
			surnames = File.ReadAllLines(surnamesPath);
		}

		public static string NextFullName()
		{
			return names[random.Next(names.Length)] + "_" + surnames[random.Next(names.Length)] + "_" + Math.Abs(new object().GetHashCode());
		}

		static Random random = new Random();

		private static string[] names;
		private static string[] surnames;

		private const string namesPath = "static/names";
		private const string surnamesPath = "static/surnames";
	}
}
