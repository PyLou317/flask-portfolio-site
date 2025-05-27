"use_strict";

const changingWordElement = document.getElementById('changing-word');
const words = ["Developer", "Salesperson", "Student"];
let currentIndex = 0;

function changeWord() {
  changingWordElement.textContent = words[currentIndex];
  currentIndex = (currentIndex + 1) % words.length; // Cycle through the array
}

setInterval(changeWord, 2000); // Change word every 2 seconds (2000 milliseconds)