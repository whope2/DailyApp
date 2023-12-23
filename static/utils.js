function newquote(element_id, category)
{
  let xmlHttpReq = new XMLHttpRequest();

  let url = "https://readingisalifestyle.com/api/getquote"
  //let url = "http://localhost:5000/api/getquote"

  if( category != undefined )
    url = url + "?cat=" + category;

  xmlHttpReq.open("GET", url, false); 
  xmlHttpReq.send();
  //console.log(xmlHttpReq.responseText);
  let quote_json = JSON.parse(xmlHttpReq.responseText);
  document.getElementById(element_id).innerHTML = quote_json["quote"] + " ─" +quote_json["author"];
}
function copy(element_id)
{
  var quote_text = document.getElementById(element_id).innerHTML;
  navigator.clipboard.writeText(quote_text);
  //alert("copied: " + quote_text);
} 

function updatebook(element_book_text, element_book_image_href, element_book_image)
{
  let xmlHttpReq = new XMLHttpRequest();
  let url = "https://readingisalifestyle.com/api/getbook"
  //let url = "http://localhost:5000/api/getbook"
  xmlHttpReq.open("GET", url, false); 
  xmlHttpReq.send();
  //console.log(xmlHttpReq.responseText);
  let json = JSON.parse(xmlHttpReq.responseText);
  document.getElementById(element_book_text).innerHTML = 
    "Title: " + json["title"] + ". " 
  + "Author: " + json["author"] + ". " 
  + "Year Published: " + json["year"] + "<br>";
  document.getElementById(element_book_image).src=`static/books/${json["image"]}`;
  document.getElementById(element_book_image_href).href=`static/books/${json["image"]}`;
}

//Update entire innerHTML replacing instagram embedded view
function updatephoto(element_photo)
{
  let xmlHttpReq = new XMLHttpRequest();
  let url = "https://readingisalifestyle.com/api/getphoto"
  //testing
  //let url = "http://localhost:5001/api/getphoto"
  xmlHttpReq.open("GET", url, false); 
  xmlHttpReq.send();
  //console.log(xmlHttpReq.responseText);
  let json = JSON.parse(xmlHttpReq.responseText);
  let src=`static/instagram/${json["image"]}`;
  document.getElementById(element_photo).innerHTML = 
    `<a href=${src}><img src=${src} alt="" style="width:100%;height:auto;max-width:538px;"></a>`;
}

function quote_to_speech(element_id)
{
  let utter = new SpeechSynthesisUtterance();
  utter.lang = 'en-US';
  utter.text = document.getElementById(element_id).innerHTML;
  utter.volume = 0.5;
  // speak
  window.speechSynthesis.speak(utter); 
}