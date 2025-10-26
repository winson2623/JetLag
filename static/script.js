const form = document.getElementById("flightForm");
    const messageDiv = document.getElementById("message");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const data = {};
      for (let element of form.elements) {
        if (element.name) data[element.name] = element.value;
      }

      try {
        const response = await fetch("http://127.0.0.1:8000/generate_schedule", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data) // wrap single flight in array
      });


        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const result = await response.json();

        messageDiv.innerHTML = `Flight schedule generated successfully!`;

        // --- Fill Pre-Flight Table ---
        const preTableBody = document.querySelector("#preScheduleTable tbody");
        preTableBody.innerHTML = "";
        result.pre_flight_schedule.forEach(row => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td>${row.date}</td>
            <td>${row.sleep_start}</td>
            <td>${row.sleep_end}</td>
            <td>${row.no_caffeine_after}</td>
            <td>${row.no_nap_after}</td>
          `;
          preTableBody.appendChild(tr);
        });

        // --- Fill Post-Flight Table ---
        const postTableBody = document.querySelector("#postScheduleTable tbody");
        postTableBody.innerHTML = "";
        result.post_flight_schedule.forEach(row => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td>${row.date}</td>
            <td>${row.sleep_start || "-"}</td>
            <td>${row.sleep_end || "-"}</td>
            <td>${row.nap_cutoff || "-"}</td>
            <td>${row.get_sunlight || row.note || "-"}</td>
          `;
          postTableBody.appendChild(tr);
        });

      // Ranked table
        const rankedTableBody = document.querySelector("#rankedFlightsTable tbody");
        rankedTableBody.innerHTML = "";
        result.flights_found.forEach(flight => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${flight.rank}</td>
                <td>${flight.flight_name}</td>
                <td>${flight.total_score}</td>
                <td>${flight.departure}</td>
                <td>${flight.arrival}</td>
            `;
            rankedTableBody.appendChild(tr);
        });


      } catch (error) {
        console.error(error);
        messageDiv.innerHTML = `Failed to connect. Make sure FastAPI is running at <code>http://127.0.0.1:8000</code>`;
        messageDiv.style.color = "#c62828";
      }
    });