using System;
using System.Net;
using Electro.Crypto;
using Electro.Model;
using Electro.Utils;
using log4net;

namespace Electro.Handlers
{
	class StartElectionHandler : AuthorizedBaseHandler
	{
		private readonly ElectroController electroController;

		public StartElectionHandler(ElectroController electroController, AuthController authController, string prefix) : base(authController, prefix)
		{
			this.electroController = electroController;
		}

		protected override void ProcessAuthorizedRequest(HttpListenerContext context, User user)
		{
			context.Request.AssertMethod(WebRequestMethods.Http.Post);
			var form = context.Request.GetPostData();
			string electionName;
			string isPublicString; bool isPublic;
			string nominateDurationString; int nominateDuration;
			string voteDurationString; int voteDuration;
			if(!form.TryGetValue("name", out electionName) ||
			   !form.TryGetValue("isPublic", out isPublicString) || !bool.TryParse(isPublicString, out isPublic) ||
			   !form.TryGetValue("nominateDuration", out nominateDurationString) || !int.TryParse(nominateDurationString, out nominateDuration) || nominateDuration <= 0 ||
			   !form.TryGetValue("voteDuration", out voteDurationString) || !int.TryParse(voteDurationString, out voteDuration) || voteDuration <= 0)
			{
				throw new HttpException(HttpStatusCode.BadRequest, "Invalid request params");
			}

			var now = DateTime.UtcNow;
			var electionId = electroController.StartElection(electionName, user, isPublic, now.AddSeconds(nominateDuration), now.AddSeconds(nominateDuration + voteDuration));

			var election = electroController.FindElectionForUser(electionId, user);
			WriteData(context, election.ToJson());

			log.InfoFormat("Started election '{0}''", election.Id);
		}

		private static readonly ILog log = LogManager.GetLogger(typeof(StartElectionHandler));
	}
}
