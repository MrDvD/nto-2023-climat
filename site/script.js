timeout = 500;

function start() {
   setTimeout(() => {
      $.ajax({
         type: "get",
         url: "/info",
         success: function(data) {
            obj = JSON.parse(data);
            $('#outside').html(obj['outside']);
            $('#inside').html(obj['inside']);
            $('#difference').html(obj['difference']);
            $('#fan').html(obj['fan']);
            $('#window').html(obj['window']);
         }
      });
      start();
   }, timeout);
}

start();

$('#ok').on('click', function() {
   parsed = parseInt($('#timeout').val())
   if (parsed && Number.isInteger(parsed)) {
      timeout = parsed;
   } else {
      alert("Incorrect frequency format");
   }
});