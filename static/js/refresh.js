$(function() {
  var stateElem = $('#state');

  function refreshState() {
    $.get(refreshUrl)
      .done(function(data) {
        var state = data.state;
        var done = data.done
        var destination = data.destination;

        stateElem.text(state);
        if (done) {
          location.href = destination;
          clearInterval(intervalId);
        }
      })
  }

  var intervalId = setInterval(refreshState, 5000);
});
