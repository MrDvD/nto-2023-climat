timeout = 500;

function start() {
   setTimeout(() => {
      $.ajax({
         type: "get",
         url: "/info",
         success: function(data) {
            obj = JSON.parse(data);
            $('#temp_out > #value').html(obj['outdoors']);
            $('#temp_in > #value').html(obj['indoors']);
            $('#temp_diff > #value').html(obj['difference']);
            $('#fan_duty > #value').html(obj['fan']);
            $('#window_state > #value').html(obj['window']);
         }
      });
      start();
   }, timeout);
}

start();

$('#ok').on('click', function() {
   parsed = parseInt($('#timeout').val());
   if (parsed && Number.isInteger(parsed)) {
      timeout = parsed;
   } else {
      alert("Incorrect frequency format");
   }
});

function asdf() {
   alert('asdasd');
}

var item = document.getElementsByID('.temp_out > button:nth-child(4)');
item.on('click', function() {
   alert('yay');
});

// $('#temp_out') {
//    function() {
//       $('this.#lock').on('click', function() {
//          alert('asdasd');
//          parsed = parseFloat($('#temp_out > #value').val());
//          if (parsed && Number.isFloat(parsed)) {
//             $.ajax({
//                type: "post",
//                url: "/outdoors",
//                data: parsed
//             });
//          } else {
//             alert("Incorrect temperature format");
//          }
//       });
//    }
// };

$('#temp_in > #lock').on('click', function() {
   parsed = parseFloat($('#temp_in > #value').val());
   if (parsed && Number.isFloat(parsed)) {
      $.ajax({
         type: "post",
         url: "/indoors",
         data: parsed
      });
   } else {
      alert("Incorrect Temperature format");
   }
});

$('#fan_duty > #lock').on('click', function() {
   parsed = parseInt($('#fan_duty > #value').val());
   if (parsed && Number.isInt(parsed) && parsed >= 0 && parsed <= 100) {
      $.ajax({
         type: "post",
         url: "/fan",
         data: parsed
      });
   } else {
      alert("Incorrect Fan Duty format");
   }
});

$('#window_state > #lock').on('click', function() {
   parsed = parseInt($('#window_state > #value').val());
   if (parsed && Number.isFloat(parsed) && parsed >= 0 && parsed <= 1) {
      $.ajax({
         type: "post",
         url: "/window",
         data: parsed
      });
   } else {
      alert("Incorrect Window State format");
   }
});

$('#temp_out > #unlock').on('click', function() {
   $.ajax({
      type: "post",
      url: "/unoutdoors",
   });
});

$('#temp_in > #unlock').on('click', function() {
   $.ajax({
      type: "post",
      url: "/unindoors",
   });
});

$('#fan_duty > #unlock').on('click', function() {
   $.ajax({
      type: "post",
      url: "/unfan",
   });
});

$('#window_state > #unlock').on('click', function() {
   $.ajax({
      type: "post",
      url: "/unwindow",
   });
});