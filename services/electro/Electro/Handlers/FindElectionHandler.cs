using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using Electro.Model;
using Electro.Utils;
using log4net;

namespace Electro.Handlers
{
	class FindElectionHandler : AuthorizedBaseHandler
	{
		private readonly ElectroController electroController;

		public FindElectionHandler(ElectroController electroController, AuthController authController, string prefix) : base(authController, prefix)
		{
			this.electroController = electroController;
		}

		protected override void ProcessAuthorizedRequest(HttpListenerContext context, User user)
		{
			var idString = context.Request.QueryString["id"];
			Guid id;
			if(!Guid.TryParse(idString, out id))
				throw new HttpException(HttpStatusCode.BadRequest, string.Format("Invalid election id '{0}'", idString));

			var election = electroController.FindElectionForUser(id, user);
			if(election == null)
				throw new HttpException(HttpStatusCode.NotFound, string.Format("Can't find election with id '{0}'", id));

			WriteData(context, election.ToJson());

			log.InfoFormat("Found election '{0}'", id);
		}

		private static readonly ILog log = LogManager.GetLogger(typeof(FindElectionHandler));
	}
}
