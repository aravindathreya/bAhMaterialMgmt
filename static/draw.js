const { PDFDocument, StandardFonts, rgb } = PDFLib

$(document).ready(function () {
  if ($('#canvas').length)
    initialize();
});

// works out the X, Y position of the click inside the canvas from the X, Y position on the page

// function getPosition(mouseEvent, sigCanvas) {
//   var rect = sigCanvas.getBoundingClientRect();
//   return {
//     X: mouseEvent.clientX - rect.left,
//     Y: mouseEvent.clientY - rect.top
//   };
// }

function getPosition(mouseEvent, sigCanvas) {
  var x, y;

  var rect = sigCanvas.getBoundingClientRect();
  if (mouseEvent.pageX != undefined && mouseEvent.pageY != undefined && mouseEvent.pageX != 0 && mouseEvent.pageY != 0) {
    x = mouseEvent.pageX;
    y = mouseEvent.pageY;

  } else {

    x = mouseEvent.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
    y = mouseEvent.clientY + document.body.scrollTop + document.documentElement.scrollTop;

  }

  return {
    X: x - rect.left,
    Y: y - rect.top
  };
}

function initialize() {
  // get references to the canvas element as well as the 2D drawing context
  var sigCanvas = document.getElementById("canvas");
  var context = sigCanvas.getContext("2d");
  context.strokeStyle = "#000000";
  context.lineJoin = "round";
  context.lineWidth = 3;

  // This will be defined on a TOUCH device such as iPad or Android, etc.
  var is_touch_device = 'ontouchstart' in document.documentElement;

  if (is_touch_device) {
    // create a drawer which tracks touch movements
    var drawer = {
      isDrawing: false,
      touchstart: function (coors) {
        context.beginPath();
        context.moveTo(coors.x, coors.y);
        this.isDrawing = true;
      },
      touchmove: function (coors) {
        if (this.isDrawing) {
          context.lineTo(coors.x, coors.y);
          context.stroke();
          console.log(coors)
        }
      },
      touchend: function (coors) {
        if (this.isDrawing) {
          this.touchmove(coors);
          this.isDrawing = false;
        }
      }
    };

    // create a function to pass touch events and coordinates to drawer
    function draw(event) {

     

      // get the touch coordinates.  Using the first touch in case of multi-touch
      if (parseInt(event.changedTouches[0].clientX) > 0 && parseInt(event.changedTouches[0].clientY) > 0) {
        var coors = {
          clientX: event.changedTouches[0].clientX,
          clientY: event.changedTouches[0].clientY,
          x: event.changedTouches[0].clientX,
          y: event.changedTouches[0].clientY
        };
  
        var mouseEvent = new MouseEvent("mousemove", coors);
        sigCanvas.dispatchEvent(mouseEvent);
  
      }
      
      // // Now we need to get the offset of the canvas location
      // var obj = sigCanvas;

      // if (obj.offsetParent) {
      //   // Every time we find a new object, we add its offsetLeft and offsetTop to curleft and curtop.
      //   do {
      //     coors.x -= obj.offsetLeft;
      //     coors.y -= obj.offsetTop;
      //   }
      //   // The while loop can be "while (obj = obj.offsetParent)" only, which does return null
      //   // when null is passed back, but that creates a warning in some editors (i.e. VS2010).
      //   while ((obj = obj.offsetParent) != null);
      // }

      // // pass the coordinates to the appropriate handler
      // drawer[event.type](coors);
    }

    // attach the touchstart, touchmove, touchend event listeners.
    sigCanvas.addEventListener('touchstart', draw, false);
    sigCanvas.addEventListener('touchmove', draw, false);
    sigCanvas.addEventListener('touchend', draw, false);

    // prevent elastic scrolling
    sigCanvas.addEventListener('touchmove', function (event) {
      event.preventDefault();
    }, false);
  } 

    // start drawing when the mousedown event fires, and attach handlers to
    // draw a line to wherever the mouse moves to
    $("#canvas").on('mousedown pointerdown', function (mouseEvent) {
      var position = getPosition(mouseEvent, sigCanvas);
      context.moveTo(position.X, position.Y);
      context.beginPath();

      // attach event handlers
      $(this).on('mousemove pointermove',function (mouseEvent) {
        drawLine(mouseEvent, sigCanvas, context);
      }).on('mouseup pointerup',function (mouseEvent) {
        finishDrawing(mouseEvent, sigCanvas, context);
      }).on('mouseout pointerout',function (mouseEvent) {
        finishDrawing(mouseEvent, sigCanvas, context);
      });
    });

}

// draws a line to the x and y coordinates of the mouse event inside
// the specified element using the specified context
function drawLine(mouseEvent, sigCanvas, context) {

  var position = getPosition(mouseEvent, sigCanvas);


  context.lineTo(position.X, position.Y);
  context.stroke();
}

// draws a line from the last coordiantes in the path to the finishing
// coordinates and unbind any event handlers which need to be preceded
// by the mouse down event
function finishDrawing(mouseEvent, sigCanvas, context) {
  // draw the line to the finishing coordinates
  drawLine(mouseEvent, sigCanvas, context);

  context.closePath();

  // unbind any events which could draw
  $(sigCanvas).unbind("mousemove pointermove")
    .unbind("mouseup pointerup")
    .unbind("mouseout pointerout");
}

// Clear the canvas context using the canvas width and height
function clearCanvas() {
  var canvas = document.getElementById("canvas");
  var context = canvas.getContext("2d");
  context.clearRect(0, 0, canvas.width, canvas.height);
}

var lineHeight;
async function getAndPutAnnexure() {
  var formData = new FormData();
  formData.append("work_order_id", $('#wo_id').val())

  wo_value = parseInt($('.value').text().trim())
  $.ajax({
    type: "POST",
    url: "/get_milsetones",
    async: true,
    data: formData,
    cache: false,
    contentType: false,
    processData: false,
    timeout: 60000,
    success: function (data) {
      console.log(data)
      
      var canvas = document.getElementById("annexure_canvas");
      var context = canvas.getContext("2d");
      context.font = "14px Arial";
      lines = (data.length * 20) + 100
      lineHeight = lines
      $(canvas).attr('height', lines.toString() +'px')

      x = 20;
      y = 20;
      for (const stage of data) {
        context.fillText(stage[0], x, y);
        x = 500;
        context.fillText(stage[1].toString()+'%', x, y);
        x = 600
        const amount = (parseFloat(stage[1]) / 100) * wo_value
        context.fillText('₹ '+amount.toString(), x, y);
        y += 20;
        x = 20;
      }
    },
    error: function (error) {
      console.log(error)
    },
  });

}

async function saveSign() {
  $('.create-wo-btn').attr('disabled','true')
  $('.create-wo-btn').text('Submitting..')
  if($('.verification_code').text().length) {
    entered_code = $('#entered_code').val()
    if (entered_code.trim() != $('.verification_code').text().trim()) {
      alert('Invalid verification code')
      $('.create-wo-btn').removeAttr('disabled')
      $('.create-wo-btn').text('Submit')
      return false;
    }
  }
  getAndPutAnnexure()
  var canvas = document.getElementById("canvas");
  var ctx = canvas.getContext("2d");
  let pngImageBytes = canvas.toDataURL("image/png");


  const url = 'https://app.buildahome.in/static/Standard_WO.pdf'
  const arrayBuffer = await fetch(url).then(res => res.arrayBuffer())
  const pdfDoc = await PDFDocument.load(arrayBuffer)

  const pngImage = await pdfDoc.embedPng(pngImageBytes)
  const pngDims = pngImage.scale(0.5)

  var annexure_canvas = document.getElementById("annexure_canvas");
  var ctx1 = annexure_canvas.getContext("2d");
  let pngImageBytes1 = annexure_canvas.toDataURL("image/png");

  const pngImage1 = await pdfDoc.embedPng(pngImageBytes1)
  const pngDims1 = pngImage.scale(0.5)

  const pages = pdfDoc.getPages()

  const date = new Date()
  pages[0].drawText(date.getDate() + '/' + (parseInt(date.getMonth()) + 1).toString() + '/' + date.getFullYear(), {
    x: 448,
    y: 698,
    size: 11,
  })

  const wo_number = $('.wo_number').text().trim()
  pages[0].drawText(wo_number, {
    x: 448,
    y: 676,
    size: 10,
    lineHeight: 13,
  })

  const contractor_name = $('.contractor_name').text().trim()
  pages[0].drawText(contractor_name, {
    x: 448,
    y: 655,
    size: 11,
  })

  const contractor_address = $('.contractor_address').text().trim()
  pages[0].drawText(contractor_address, {
    x: 448,
    y: 609,
    size: 10,
    lineHeight: 13,
    maxWidth: 150,
  })

  const contractor_pan = $('.contractor_pan').text().trim()
  pages[0].drawText(contractor_pan, {
    x: 448,
    y: 553,
    size: 11,
  })

  const cheque_number = $('.cheque_number').text().trim()
  pages[0].drawText(cheque_number, {
    x: 448,
    y: 534,
    size: 11,
  })

  const contractor_code = $('.contractor_code').text().trim()
  pages[0].drawText(contractor_code, {
    x: 448,
    y: 514,
    size: 11,
  })

  const description = $('.trade').text().trim() + ' work order for ' + $('.project_name').text().trim()
  pages[0].drawText(description, {
    x: 100,
    y: 410,
    size: 11,
  })

  if($(".total_bua").text().trim().length && $(".cost_per_sqft").text().trim().length) {
    const total_bua = $(".total_bua").text().trim() 
    const cost_per_sqft = $(".cost_per_sqft").text().trim() 
    pages[0].drawText('Total BUA :'+total_bua.toString()+', Cost/sqft : '+cost_per_sqft.toString(), {
      x: 100,
      y: 395,
      size: 11,
    })
  }

  const value = $('.value').text().trim()
  pages[0].drawText(value, {
    x: 448,
    y: 410,
    size: 11,
  })

  const notes = $(".contractor_notes").text().trim()
  const notesList = notes.split('\n')
  var yCord = pages[3].getSize().height - 120;
  for(const note of notesList) {
    pages[3].drawText(note.trim(), {
      x: 100,
      y: yCord,
      size: 10,
      lineHeight: 12,
      maxWidth: pages[3].getSize().width - 150,
    })
    noOfLines = parseInt(note.trim().length / 100)
    yCord = yCord - (14 * noOfLines)
    yCord = yCord - 20;
  } 
  

  pages[4].drawImage(pngImage, {
    x: 330,
    y: 140,
    width: 100,
    height: 50,
  })

  const sealUrl = 'https://app.buildahome.in/static/seal.png'
  const sealImgBytes = await fetch(sealUrl).then((res) => res.arrayBuffer())

  const sealImg = await pdfDoc.embedPng(sealImgBytes)

  pages[4].drawImage(sealImg, {
    x: 40,
    y: 90,
    width: 70,
    height: 100,
  })
  
  pages[4].drawImage(pngImage1, {
    x: 40,
    y: pages[4].getSize().height - 110  - parseInt(lineHeight * 0.8),
    width: parseInt(550 * 0.8),
    height: parseInt(lineHeight * 0.8),
  })




  const pdfBytes = await pdfDoc.save()


  const blob = new Blob([pdfBytes])
  var file = new File([blob], 'test.pdf');

  var formData = new FormData();
  formData.append("wo_id", $('#wo_id').val())

  formData.append("project_name", $('.project_name').text().trim())
  formData.append("trade", $('.trade').text().trim())
  formData.append("contractor_name", $('.contractor_name').text().trim())

  formData.append("file", file, 'test.pdf');

  $.ajax({
    type: "POST",
    url: "/upload_signed_wo",
    success: function (data) {
      window.location.href = '/view_unsigned_work_order'
    },
    error: function (error) {
      console.log(error)
      // handle error
    },
    async: true,
    data: formData,
    cache: false,
    contentType: false,
    processData: false,
    timeout: 60000
  });

  // Trigger the browser to download the PDF document
  // download(pdfBytes, "signed_wo.pdf", "application/pdf");



}

