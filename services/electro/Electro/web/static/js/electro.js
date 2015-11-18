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

    $.fn.prepare_template = function(selector) {
        selector = selector || '*';
        return this.children(':not([id$=-template])').filter(selector).remove();
    };

    var crypto = {        
        encrypt: function(vote_vector, public_key) {
            var self = this;
            return $.map(vote_vector, function(idx, vote_element){
                return self.encrypt_bit(vote_element, public_key).toString();
            });            
        },

        encrypt_bit: function(bit, public_key) {
            var bigInts = $.map(this.random_subset(public_key.keyParts), function(obj) {
                    return bigInt(obj);
            });

            var sum = bigInts.reduce(function(prev, current) {
                return prev.add(current);
            }, bigInt.zero);

            return sum.add(bigInt.randBetween(10, 100).multiply(public_key.MaxNum)).add(bit)
        },

        random_subset: function(set) {
            return $.grep(set, function(){
                return Math.floor(Math.random() * 2) == 0;
            });
        },
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
            $('#election').data('election-id', election.Id);
            $('#election').data('election-public-key', election.PublicKey);
            $('#election .election--candidates').prepare_template('.election--candidate');

            $('.election--name').text(election.Name);
            $('.election--nominate-till').text(election.nominateTill);
            $('.election--vote-till').text(election.voteTill);

            $('#election').toggleClass('election-nomination-finished', election.IsNominationFinished);
            $('#election').toggleClass('election-finished', election.IsFinished);
            
            var $candidate_template = $('#election--canditate--template');
            $.each(election.candidates, function(idx, candidate) {
                var $clone = $candidate_template.clone().removeAttr('id');
                $clone.data('candidate-idx', idx);
                $clone.find('.election--candidate--name').text(candidate.Name);
                if (election.DecryptedResult && election.DecryptedResult[idx])
                    $clone.find('.election--candidate--result').text(election.DecryptedResult[idx]);
                if (candidate.PrivateNotesForWinner)
                    $clone.find('.election--candidate--private-note').text(candidate.PrivateNotesForWinner);
                $candidate_template.parent().append($clone);
            });

            $('.election--votes').prepare_template('.election--vote');
            $('.election--vote').prepare_template();
            $vote_template = $('#election--vote--template');
            $vote_candidate_template = $('#election--vote--candidate--template');
            $.each(election.votes, function(idx, vote) {
                var $clone = $vote_template.clone().removeAttr('id');
                $.each(vote.encryptedVector, function(idx, vote_candidate) {
                    var $clone_vote_candidate = $vote_candidate_template.clone().removeAttr('id');
                    $clone_vote_candidate.text(vote_candidate);
                    $clone.append($clone_vote_candidate);
                });
                $vote_template.parent().append($clone);
            });

            $('.election--votes').toggleClass('empty', election.votes.length == 0);
        },

        load_elections: function(callback) {
            var self = this;
            $('#elections').prepare_template('.election');
            $.getJSON('/listElections?finished=false', function(data) {
                $.each(data, function(idx, election) {
                    self.show_elections_election(election);
                });

                // TODO: add stub "Finished: "

                $.getJSON('/listElections?finished=true', function(data) {
                    $.each(data, function(idx, election) {
                        self.show_elections_election(election);
                    });
                    self.update_handlers();
                    callback();
                });
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

            $('.home-link').unbind('click').click(function(){
                self.init();
                return false;
            });

            $('.elections--election--link').unbind('click').click(function(){
                self.load_election($(this).data('election-id'));
                return false;
            });

            $create_election_form = $('#create-election--form');
            $create_election_form.find('button').unbind('click').click(function(){
                $.post('/startElection', $create_election_form.serialize_form(), function(election){
                    self.load_election(election.Id);
                }, 'json');
                return false;
            });

            $('.election--nominate-button button').unbind('click').click(function() {
                election_id = $('#election').data('election-id');
                $.post('/nominate', {'electionId': election_id}, function(election){
                    self.load_election(election.Id)
                }, 'json');
                return false;
            });

            $('.election--candidate--vote-button button').unbind('click').click(function(){
                var $candidate = $($(this).parents('.election--candidate')[0]);
                var candidate_idx = $candidate.data('candidate-idx');
                var candidates_count = $candidate.parent().children('.election--candidate').length - 1
                var election_id = $('#election').data('election-id');
                var public_key = $('#election').data('election-public-key');
                
                var vote_vector = [];
                for (var i = 0; i < candidates_count; i++)
                    if (i == candidate_idx)
                        vote_vector.push(1);
                    else
                        vote_vector.push(0);

                var encrypted_vote = crypto.encrypt(vote_vector, public_key);
                $.post('vote', {'electionId': election_id, 'vote': JSON.stringify(encrypted_vote)}, function(data){
                    self.load_election(election_id);
                });
            });

            $('.show-register-button').unbind('click').click(function(){
                $('#register').set_current();
                return false;
            });

            $('.show-login-button').unbind('click').click(function(){
                $('#login').set_current();
                return false;
            });

            $('.login-button').unbind('click').click(function(){
                $.post('/login', $(this).parent().serialize_form(), function(){
                    self.init();
                });
                return false;
            });

            $('.register-button').unbind('click').click(function(){
                $.post('/register', $(this).parent().serialize_form(), function(){
                    self.init();
                });
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
                this.update_handlers();
            }
        },
    }

    $(document).ready(function(){
        electro.init();        

        $('input[type=checkbox]').switcher();

        $(document).ajaxError(function(event, jqxhr, settings, thrownError) {
            if (jqxhr.status == 401) {
            }
            $('.error-message').text(jqxhr.statusText).show().fadeOut(2000, 'easeInQuart');
            return false;
        });
    });
})(jQuery);
