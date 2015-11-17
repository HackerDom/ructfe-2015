using System;

namespace Electro.Utils
{
	internal static class CommonUtils
	{
		public static void Try(Action action)
		{
			try
			{
				action();
			}
			catch(Exception) { }
		}

		public static T TryOrDefault<T>(Func<T> func)
		{
			try
			{
				return func();
			}
			catch
			{
				return default(T);
			}
		}
	}
}