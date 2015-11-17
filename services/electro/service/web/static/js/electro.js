if (! String.prototype.startsWith) {
  Object.defineProperty(String.prototype, 'startsWith', {
    enumerable: false,
    configurable: false,
    writable: false,
    value: function(searchString, position) {
      position = position || 0;
      return this.lastIndexOf(searchString, position) === position;
    }
  });
}

(function($){
    $.fn.set_current = function() {
        $('.electro-block').hide();
        return this.each(function() {
            $(this).show();
        });
    };

    $.fn.serialize_form = function() {
        var values = $(this).serializeArray();
        values = values.concat(
            $(this).find('input[type=checkbox]').map(function() {
                        console.log($(this));
                        return {"name": this.name, "value": $(this).is(':checked')}
                    }).get()
        );

        return values;
    };

    var electro = {
        is_auth: function() {
            return document.cookie.startsWith('login=');
        },

        show_elections_election: function(election) {
            var $template = $('#elections--election--template');
            var $clone = $template.clone().removeAttr('id');

            var election_link = $('<a href="#">').addClass('elections--election--link').data('election-id', election.Id).text(election.Name);
            $clone.find('.elections--election--name').append(election_link);
            $clone.find('.elections--election--nominate-till').text(election.nominateTill);
            $clone.find('.elections--election--vote-till').text(election.voteTill);
            if (election.Winner)
                $clone.find('.elections--election--winner').text(election.Winner.Name);
            $template.parent().append($clone);
        },

        show_election: function(election) {
            $('.election--name').text(election.Name);
            $('.election--nominate-till').text(election.nominateTill);
            $('.election--vote-till').text(election.voteTill);
            if (election.IsNominationFinished)
                $('#election').addClass('election-nomination-finished')
            if (election.IsFinished)
                $('#election').addClass('election-finished')
            
            var $candidate_template = $('#election--canditate--template');
            $.each(election.candidates, function(idx, candidate) {
                var $clone = $candidate_template.clone().removeAttr('id');
                $clone.find('.election--candidate--name').text(candidate.Name);
                if (election.DecryptedResult && election.DecryptedResult[idx])
                    $clone.find('.election--candidate--result').text(election.DecryptedResult[idx]);
                if (candidate.PrivateNotesForWinner)
                    $clone.find('.election--candidate--private-note').text(candidate.PrivateNotesForWinner);
                $candidate_template.parent().append($clone);
            });

            $vote_template = $('#election--vote--template');
            $vote_candidate_template = $('#election--vote--candidate--template');
            $.each(election.votes, function(idx, vote) {
                var $clone = $vote_template.clone().removeAttr('id');
                $.each(vote.encryptedVector, function(idx, vote_candidate) {
                    var $clone_vote_candidate = $vote_candidate_template.clone().removeAttr();
                    $clone_vote_candidate.text(vote_candidate)
                    $clone.append($clone_vote_candidate);
                });
                $vote_template.parent().append($clone);
            });
        },

        load_elections: function(callback) {
            var self = this;
            $.getJSON('/listElections?finished=true', function(data) {
                $.each(data, function(idx, election) {
                    self.show_elections_election(election);
                });
                self.update_handlers();
                callback();
            });
        },

        load_election: function(election_id, callback) {
            var self = this;
            $.getJSON('/findElection?id=' + election_id, function(election){
                self.show_election(election);
                self.update_handlers();

                $('#election').set_current();
                if (callback)
                    callback();
            });
        },

        update_handlers: function() {
            var self = this;
            $('.elections--election--link').click(function(){
                self.load_election($(this).data('election-id'));
            });

            $create_election_form = $('#create-election--form');
            $create_election_form.find('button').click(function(){
                $.post('/startElection', $create_election_form.serialize_form(), function(election){
                    self.load_election(election.Id);
                }, 'json');
                return false;
            });
        },

        init: function() {            
            if (electro.is_auth()) {
                this.load_elections(function(){
                    $('#elections').set_current();
                });
            } else {
                $('#login').set_current();
            }
        },
    }

    $(document).ready(function(){
        electro.init();
    });
})(jQuery);
