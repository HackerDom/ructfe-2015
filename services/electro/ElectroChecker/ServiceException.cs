using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ElectroChecker
{
	class ServiceException : Exception
	{
		public ExitCode code;
		public string publicMessage;

		public ServiceException(ExitCode code, string privateMes, string publicMessage = null) : base(privateMes)
		{
			this.code = code;
			this.publicMessage = publicMessage;
		}
	}
}
