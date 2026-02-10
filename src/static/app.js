document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message and activities list
      activitiesList.innerHTML = "";
      
      // Clear activity dropdown options (keep only the first placeholder option)
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;


        // Create activity content elements safely without using innerHTML
        const titleEl = document.createElement("h4");
        titleEl.textContent = name;

        const descriptionEl = document.createElement("p");
        descriptionEl.textContent = details.description;

        const scheduleEl = document.createElement("p");
        const scheduleStrong = document.createElement("strong");
        scheduleStrong.textContent = "Schedule:";
        scheduleEl.appendChild(scheduleStrong);
        scheduleEl.appendChild(document.createTextNode(" " + details.schedule));

        const availabilityEl = document.createElement("p");
        const availabilityStrong = document.createElement("strong");
        availabilityStrong.textContent = "Availability:";
        availabilityEl.appendChild(availabilityStrong);
        availabilityEl.appendChild(document.createTextNode(" " + spotsLeft + " spots left"));

        // Create participants section
        const participantsSection = document.createElement("div");
        participantsSection.className = "participants-section";

        if (details.participants && details.participants.length > 0) {
          const participantsLabel = document.createElement("strong");
          participantsLabel.textContent = "Participants:";
          participantsSection.appendChild(participantsLabel);

          const participantsList = document.createElement("ul");
          participantsList.className = "participants-list";

          details.participants.forEach(p => {
            const li = document.createElement("li");

            const emailSpan = document.createElement("span");
            emailSpan.className = "participant-email";
            emailSpan.textContent = p;

            const deleteBtn = document.createElement("button");
            deleteBtn.className = "delete-btn";
            deleteBtn.dataset.activity = name;
            deleteBtn.dataset.email = p;
            deleteBtn.title = "Unregister " + p;
            deleteBtn.textContent = "✕";

            li.appendChild(emailSpan);
            li.appendChild(deleteBtn);
            participantsList.appendChild(li);
          });

          participantsSection.appendChild(participantsList);
        } else {
          participantsSection.classList.add("empty");
          const noParticipantsEm = document.createElement("em");
          noParticipantsEm.textContent = "No participants yet";
          participantsSection.appendChild(noParticipantsEm);
        }

        // Assemble card
        activityCard.appendChild(titleEl);
        activityCard.appendChild(descriptionEl);
        activityCard.appendChild(scheduleEl);
        activityCard.appendChild(availabilityEl);
        activityCard.appendChild(participantsSection);

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Add event listeners to all delete buttons
      document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', handleUnregister);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle unregister action
  async function handleUnregister(event) {
    const activity = event.target.dataset.activity;
    const email = event.target.dataset.email;

    if (!confirm(`Are you sure you want to unregister ${email} from ${activity}?`)) {
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        messageDiv.classList.remove("hidden");

        // Refresh the activities list
        await fetchActivities();

        // Hide message after 5 seconds
        setTimeout(() => {
          messageDiv.classList.add("hidden");
        }, 5000);
      } else {
        messageDiv.textContent = result.detail || "Failed to unregister";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
      }
    } catch (error) {
      messageDiv.textContent = "Failed to unregister. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        
        // Refresh the activities list to show the new participant
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
