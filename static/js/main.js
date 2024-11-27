const inputTranscription = document.getElementById("inputTranscription");
const outputTranscription = document.getElementById("outputTranscription");
const startButton = document.getElementById("startButton");
const stopButton = document.getElementById("stopButton");
const speakButton = document.getElementById("speakButton");

let recognition;

if ('webkitSpeechRecognition' in window) {
  recognition = new webkitSpeechRecognition();
} else if ('SpeechRecognition' in window) {
  recognition = new SpeechRecognition();
}

if (recognition) {
  recognition.continuous = true; // Capture continuously
  recognition.interimResults = true; // Capture partial results

  recognition.onresult = function(event) {
    let interimTranscript = '';
    let finalTranscript = '';

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += transcript + ' ';
      } else {
        interimTranscript += transcript;
      }
    }

    // Display real-time input transcription
    inputTranscription.value = finalTranscript + interimTranscript;
  };

  recognition.onerror = function(event) {
    console.error('Speech recognition error:', event.error);
  }
}

// Start recording
startButton.addEventListener('click', () => {
  // Get the selected language for speech recognition
  const selectedLanguage = document.getElementById("inputLanguage").value;

  // Set the language for speech recognition
  recognition.lang = selectedLanguage; // Example: 'fr-FR' for French or 'en-US' for English

  recognition.start();
  startButton.disabled = true;
  stopButton.disabled = false;
});

// Stop recording
stopButton.addEventListener('click', () => {
  recognition.stop();
  startButton.disabled = false;
  stopButton.disabled = true;

  // Check if the input field has content before starting translation
  const inputText = inputTranscription.value.trim();
  if (inputText) {
    translateText(inputText);  // Translate only if there's text
  }
});

// Translate text (calls the backend API)
async function translateText(inputText) {
  const sourceLang = document.getElementById("inputLanguage").value;
  const targetLang = document.getElementById("outputLanguage").value;

  const response = await fetch('/translate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      text: inputText,
      sourceLang: sourceLang,
      targetLang: targetLang
    })
  });

  const result = await response.json();
  if (result.translatedText) {
    outputTranscription.value = result.translatedText;
  } else {
    outputTranscription.value = "Error: Translation failed";
  }
}
speakButton.addEventListener('click', async () => {
  console.log("Speak button clicked!"); // Debug log
  await speakTranslatedText(); // Call the function
});
async function speakTranslatedText() {
  const translatedText = outputTranscription.value;
  console.log("Translated Text:", translatedText); // Debug log

  // Get the target language for TTS
  const targetLang = document.getElementById("outputLanguage").value;
  console.log("Target Language:", targetLang); // Debug log

  try {
      const response = await fetch('/speak', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({
              translatedText,
              targetLang // Send the target language along with the translated text
          })
      });

      if (!response.ok) {
          const errorData = await response.json();
          if (errorData.error) {
              alert(errorData.message); // Show the error message in a popup
          }
          throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Audio data received:", data.audioContent); // Debug log

      if (data.audioContent) {
          const audio = new Audio(`data:audio/mp3;base64,${data.audioContent}`);
          audio.play();
      } else {
          console.error("Error: No audio content received.");
      }
  } catch (error) {
      console.error("Error in speakTranslatedText:", error);
  }
}

