using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Numerics;
using System.Text;
using System.Threading.Tasks;
using Electro.Model;
using Electro.Utils;

namespace Electro.Handlers
{
	class VoteHandler : AuthorizedBaseHandler
	{
		private readonly ElectroController electroController;

		public VoteHandler(ElectroController electroController, AuthController authController, string prefix) : base(authController, prefix)
		{
			this.electroController = electroController;
		}

		protected override void ProcessAuthorizedRequest(HttpListenerContext context, User user)
		{
			context.Request.AssertMethod(WebRequestMethods.Http.Post);
			var form = context.Request.GetPostData();

			string electionIdString; Guid electionId;
			string voteArrayString; string[] voteStringArray; BigInteger[] voteArray;
			if(!form.TryGetValue("electionId", out electionIdString) || !Guid.TryParse(electionIdString, out electionId) ||
				!form.TryGetValue("vote", out voteArrayString) || (voteStringArray = JsonHelper.TryParseJson<string[]>(voteArrayString)) == null || (voteArray = ParseVoteArray(voteStringArray)) == null)
				throw new HttpException(HttpStatusCode.BadRequest, "Invalid request params");

			var success = electroController.Vote(electionId, user, voteArray);
			if(!success)
				throw new HttpException(HttpStatusCode.BadRequest, "Vote FAILED");

			WriteString(context, "Vote OK");
		}

		private BigInteger[] ParseVoteArray(string[] votesStringArray)
		{
			var failed = false;
			var result = votesStringArray.Select(s =>
			{
				BigInteger votePart;
				if(!BigInteger.TryParse(s, out votePart))
					failed = true;
				return votePart;
			}).ToArray();
			return !failed ? result : null;
		}
	}
}
