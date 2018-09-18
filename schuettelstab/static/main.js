$(document).ready(function() {
  fetchPicture();
  $('#submit').click(submitPicture);
  $('#clear').click(clearPicture);
  $('#selector').on('change', function() {
    fetchPicture(this.value)
  });
});



function drawPicture(data) {
  // TODO draw colors
  $('#artname').val(data.artname);
  var html = '';
  for(var x=0; x<data.pic.length; x++) {
    html += '<div class="column" x="' + x + '">';
    for(var y=0; y<data.pic[x].length; y++) {
      html += '<div x="' + x + '" y= "' + y + '" class="pixel btn" style="background-color: ' + data.pic[x][y] + ';"></div>';
    }
    html += '</div>';
  }
  $('#strobe').html(html);
  $('.pixel').click(function() {
    $(this).css('background-color', $('#color').val());
  });
}  
  

function fetchPicture(filename) {
  var url = '/strobe';
  if(filename) {
    url += '?filename=' + filename;
  }
  $.ajax(url, {
    method: 'GET',
    success: drawPicture,
    error: function() {
      $('h2').text('Error accessing PI');
      }
  });
}

function clearPicture() {
  $('.pixel').css('background-color', '#000000');
}

var hexDigits = new Array
        ("0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"); 

//Function to convert hex format to a rgb color
function rgb2hex(rgb) {
 rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
 return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
}

function hex(x) {
  return isNaN(x) ? "00" : hexDigits[(x - x % 16) / 16] + hexDigits[x % 16];
 }



function submitPicture() {
  var array = [];
  $('.pixel').each(function() {
    var x = parseInt($(this).attr('x'));
    var y = parseInt($(this).attr('y'));
    var color = rgb2hex($(this).css('background-color'));
      
    try {
      array[x][y] = color;
    } catch(err) {
      var tmp = [];
      tmp[y] = color;
      array[x] = tmp;
    }
  });
  var artname = $('#artname').val();

  $.ajax('/strobe', {
    method: 'POST',
    data: JSON.stringify({artname: artname, pic: array}),
    dataType: 'json',
    contentType: 'application/json',
    success: function(data) {
      $('#message').text('successfully changed picture');
      $('#message').removeClass('hide');
      setTimeout(5000, function() {
        $('#message').addClass('hide');
      });
    }
  });
}
