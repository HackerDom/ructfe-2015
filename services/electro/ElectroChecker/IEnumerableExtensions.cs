using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ElectroChecker
{
	static class IEnumerableExtensions
	{
		public static int IndexOf<T>(this IEnumerable<T> enumerable, Func<T, bool> predicate)
		{
			int result = 0;
			var enumerator = enumerable.GetEnumerator();
			while(enumerator.MoveNext())
			{
				if(predicate(enumerator.Current))
					return result;
				result++;
			}
			return -1;
		}

		public static IEnumerable<T> GetEmpty<T>()
		{
			yield break;
		}

		public static IEnumerable<T> WhereNotNull<T>(this IEnumerable<T> enumerable) where T : class
		{
			return enumerable.Where(item => item != null);
		}
	}
}
