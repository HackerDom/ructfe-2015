using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using Electro.Model;
using Electro.Utils;

namespace Electro.Handlers
{
	class FindElectionHandler : BaseHttpHandler
	{
		private readonly ElectroController electroController;

		public FindElectionHandler(ElectroController electroController, string prefix) : base(prefix)
		{
			this.electroController = electroController;
		}

		protected override void ProcessRequest(HttpListenerContext context)
		{
			var idString = context.Request.QueryString["id"];
			Guid id;
			if(!Guid.TryParse(idString, out id))
				throw new HttpException(HttpStatusCode.BadRequest, "Invalid request params");

			var election = electroController.FindElection(id);

			WriteData(context, election.ToJson());
		}
	}
}
