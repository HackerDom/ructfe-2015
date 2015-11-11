using System;
using System.Net;

namespace Electro.Handlers
{
	//NOTE: Can't use HttpListenerException because ErrorCode has invalid value on mono
	internal class HttpException : Exception
	{
		public HttpException(HttpStatusCode status, string message)
			: base(message)
		{
			Status = status;
		}

		public HttpStatusCode Status { get; private set; }
	}
}