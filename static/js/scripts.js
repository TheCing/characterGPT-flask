// Get the sidebar
var sidebar = document.getElementById("sidebar");
var closeButton = document.getElementById("close-button");

// Add an event listener to the arrow icon
document.querySelector(".arrow-icon").addEventListener("click", function () {
  sidebar.classList.toggle("open");
});

// Add an event listener to the close button
closeButton.addEventListener("click", function () {
  sidebar.classList.remove("open");
});

document.getElementById("input-field").addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault(); // Prevents the default action (form submission)
    document.getElementById("send-button").click();
  }
});

document.getElementById("send-button").addEventListener("click", () => {
  const inputValue = document.getElementById("input-field").value;

  addNewMessage("outgoing", inputValue);
  document.getElementById("input-field").value = "";

  fetch("/post_message", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message: inputValue }),
  })
    .then((response) => response.json())
    .then((data) => {
      //   const updatedText = data.updatedText;
      const completion = data.completion;

      if (completion) {
        setTimeout(addNewMessage("incoming", completion), 2000);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });

  scrollToBottom(); // Auto-scroll to the latest added message
});

function addNewMessage(messageType, messageContent) {
  if (messageType === "incoming") {
    disableTypingIndicator();
  }

  const currentTime = new Date().toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
  const newComponent = document.createElement("div");
  newComponent.classList.add("message", `${messageType}`);
  newComponent.innerHTML = `
        <div class="content">
            <p>${messageContent}</p>
            <span class="timestamp">${currentTime}</span>
        </div>
    `;

  document.getElementById("messageList").appendChild(newComponent);

  if (messageType === "outgoing") {
    enableTypingIndicator();
  }
}

function enableTypingIndicator() {
  const typingIndicator = document.getElementById("typingIndicator");
  typingIndicator.style.display = "flex";
}

function disableTypingIndicator() {
  const typingIndicator = document.getElementById("typingIndicator");
  typingIndicator.style.display = "none";
}

function scrollToBottom() {
  const messageList = document.getElementById("messageList");
  messageList.scrollTop = messageList.scrollHeight;
}

addNewMessage("incoming", "Hello! How can I help you today?");
