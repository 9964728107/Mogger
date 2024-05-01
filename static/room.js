
    var socketio = io();

    function timer(data){
        let intervalId;
        let count = data;
        intervalId = setInterval(function () {
        count--;
        if (count == 0) {
            // window.alert("time over")
            varify();
            return;
        }
        document.getElementById("counter").textContent = count;
        }, 1000);
    }

    socketio.on("timer", (data)=>{
       document.getElementById("counter").textContent = "";
       document.getElementById("counter").textContent = `${data}secs`;
        
       if (data == 0) {
         
         varify();
         document.getElementById("counter").textContent = `Well Played`;
         return;
       }
       console.log(data)
       if(data==0){
        console.log("submit")
       }
     
    });

    socketio.on('response', function(response) {
      // Handle the response from the server
      
      console.log("Received MCQs:", response);
      addQuestionsToDOM(response);
      socketio.emit("initiateTimer", 10);

      });
   

    socketio.on('Paris', function(data) {
        console.log(data);
    });

    socketio.on("varify", function(data) {
        console.log(data);
        document.getElementById("points").innerHTML = `Points: ${JSON.stringify(data)} : `;
    });

    function varify() {
        const answerss = document.querySelectorAll(".answer");
        const answers = Array.from(answerss).map(answer => answer.textContent);
        const elements = document.querySelectorAll('input.option:checked');
        const choices = Array.from(elements).map(element => element.value);
        const data = {
            choices: choices,
            answers: answers
        };
        socketio.emit("paris", "nigger");
        console.log("data", data);
        socketio.emit("varify", data);
    }

    // Get a reference to the form
    const form = document.querySelector("form");

    // Add a submit event listener to the form
    form.addEventListener("submit", function(event) {
        const ldsRoller = document.querySelector(".default");
        ldsRoller.classList.add("lds-roller");
        ldsRoller.classList.remove("default");
        console.log("Form submitted. Adding .lds-roller. class to  'default'");
    });

    // Creating questions
    function createQuestionHTML(questionData) {
        // Create a container div for the question
        var questionDiv = document.createElement('div');
        questionDiv.classList.add('flex', 'flex-col', 'm-2', 'rounded', 'bg-sky-300');

        // Create a div for the question text
        var questionTextDiv = document.createElement('div');
        questionTextDiv.classList.add('p-1', 'qn', 'bg-sky-200', 'p-4', 'question');
        questionTextDiv.textContent = questionData.question;

        // Create an ordered list for options
        var optionsList = document.createElement('ol');
        optionsList.classList.add('list-decimal', 'list-inside', 'p-4', 'options');

        // Loop through options and create list items
        questionData.options.forEach(function(option) {
            var listItem = document.createElement('li');
            listItem.innerHTML = `<input type="checkbox" class="option" name="${questionData.question}" value="${option}" required> &nbsp; ${option}`;
            optionsList.appendChild(listItem);
        });

        // Create a paragraph for the answer
        var answerPara = document.createElement('p');
        answerPara.innerHTML = `<small class="p-1">hover for answer</small><p class="rounded p-1 bg-black transition duration-600 hover:bg-sky-300 w-fit text-center answer">${questionData.answer}</p>`;

        // Append all elements to the question div
        questionDiv.appendChild(questionTextDiv);
        questionDiv.appendChild(optionsList);
        questionDiv.appendChild(answerPara);

        return questionDiv;
    }

    // Function to add questions to the DOM
    function addQuestionsToDOM(response) {
        var questionsContainer = document.getElementById('questions-container');
        // Clear existing content
        questionsContainer.innerHTML = '';
        // Loop through response and create HTML for each question
        response.forEach(function(questionData, index) {
            var questionHTML = createQuestionHTML(questionData);
            questionsContainer.appendChild(questionHTML);
        });
    }


      socketio.on("members",(data)=>{
         let membersOl = document.getElementById("members");
         membersOl.innerHTML = "";
        
        
        data.forEach(function (name) {
        var listItem = document.createElement("li");
        listItem.classList.add('bg-sky-300','p-1','text-sm')
        listItem.innerHTML = `${name}`;
        membersOl.appendChild(listItem);
        });

      })