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
	class ListElectionsHandler : BaseHttpHandler
	{
		private readonly ElectroController electroController;

		public ListElectionsHandler(ElectroController electroController, string prefix) : base(prefix)
		{
			this.electroController = electroController;
		}

		protected override void ProcessRequest(HttpListenerContext context)
		{
			var finishedString = context.Request.QueryString["finished"];
			bool finished;
			if(!bool.TryParse(finishedString, out finished))
				throw new HttpException(HttpStatusCode.BadRequest, "Invalid request params");

			ElectionPublicCore[] elections;
			if(finished)
				elections = electroController.GetFinishedElections().Select(ElectionPublicCore.Create).ToArray();
			else
				elections = electroController.GetUnfinishedPublicElections().Select(ElectionPublicCore.Create).ToArray();

			WriteData(context, elections.ToJson());
		}
	}
}
