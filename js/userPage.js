// const canvas = document.getElementById("canvas");
const sendBtn = document.querySelector("#sendBtn");
const displayList = document.querySelector("#displayList");
const textID = document.getElementById("userId").textContent

sendBtn.addEventListener("click", () => {
  // Convert the canvas content to a data URL
  const dataURL = canvas.toDataURL("image/png");
  // console.log(dataURL);
  // Create a new image element
  const image = document.createElement("img");
  // Set the image source to the data URL
  image.src = dataURL;

  // Create a new list item
  const listItem = document.createElement("li");

  // Append the image to the list item
  listItem.appendChild(image);

  // Append the list item to the displayList ul
  displayList.appendChild(listItem);


  // Create a FormData object
  const formData = new FormData();
  formData.append('image', dataURL);
  formData.append('id', textID );

  //Send to server
  // Send the dataURL to the server
  fetch("/upload-image", {
    method: "POST",
    body: formData,
    // headers: {
    //   "Content-Type": "multipart/form-data"
    // }
  })
    .then(response => response.json())
    .then(data => {
      console.log(data.message); // Success message from the server
    })
    .catch(error => {
      console.error("Error:", error);
    });

});


// Create a new WebSocket connection
const socket = new WebSocket('ws://'+ window.location.hostname+ ':' + window.location.port +'/ws');
    
// Event listener for when the WebSocket connection is established
socket.addEventListener('open', function(event) {
  // Send data to the server
  socket.send(textID);
});



// Function to update the top half of the page with the pushed data
function updateTopHalf(data) {
  //Parse Data
  const jsonData = JSON.parse(data)

  console.log(jsonData)

  // Create a new list item
  const listItem = document.createElement("li");
  // Create a container for the image and LaTeX text
  const container = document.createElement("div");
  container.classList.add("image-container");
  // Create an image element
  const image = document.createElement("img");
  image.src = jsonData.image;
  // Create a paragraph element for the LaTeX text
  const latexText = document.createElement("p");
  latexText.textContent = jsonData.latex;

  // Append the image and LaTeX text to the container
  container.appendChild(image);
  container.appendChild(latexText);

  // Append the container to the list item
  listItem.appendChild(container);

  // Append the list item to the displayList ul
  displayList.appendChild(listItem);
}

// Event listener for when a message is received from the server
socket.addEventListener('message', function(event) {
  // Update the top half of the page with the received data
  if(event.data == 'ping'){
    
  }else{
    updateTopHalf(event.data)
  }
  
});