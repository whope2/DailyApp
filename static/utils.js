function newquote(element_id)
{
  let xmlHttpReq = new XMLHttpRequest();
  //let url = "https://whereliteraturemeetscomputing.com/api/getquote"
  let url = "http://localhost:5000/api/getquote"
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

function updatebook(element_book_text, element_book_image)
{
  let xmlHttpReq = new XMLHttpRequest();
  //let url = "https://whereliteraturemeetscomputing.com/api/getbook"
  let url = "http://localhost:5000/api/getbook"
  xmlHttpReq.open("GET", url, false); 
  xmlHttpReq.send();
  //console.log(xmlHttpReq.responseText);
  let quote_json = JSON.parse(xmlHttpReq.responseText);
  document.getElementById(element_book_text).innerHTML = 
    "Title: " + quote_json["title"] + ". " 
  + "Author: " + quote_json["author"] + ". " 
  + "Year Published: " + quote_json["year"] + "<br>";
  document.getElementById(element_book_image).src=`static/books/${quote_json["image"]}`;
}