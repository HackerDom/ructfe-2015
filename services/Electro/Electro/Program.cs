using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Electro.Handlers;
using log4net;
using log4net.Config;

namespace Electro
{
	class Program
	{
		static void Main(string[] args)
		{
			XmlConfigurator.Configure();
			try
			{
				var staticHandler = new StaticHandler(GetPrefix(null), Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "static"));
				staticHandler.Start();

				Thread.Sleep(Int32.MaxValue);
			}
			catch(Exception e)
			{
				log.Fatal(e);
			}
		}

		private static string GetPrefix(string suffix)
		{
			return string.Format("http://+:{0}/{1}", Port, suffix == null ? null : suffix + '/');
		}

		private const int Port = 3130;

		private static readonly ILog log = LogManager.GetLogger(typeof(Program));
	}
}
