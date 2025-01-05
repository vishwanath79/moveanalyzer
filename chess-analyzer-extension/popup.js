document.addEventListener('DOMContentLoaded', function() {
  const analyzeButton = document.getElementById('analyze');
  const usernameInput = document.getElementById('username');
  const filterSelect = document.getElementById('filter');
  const loadingSpinner = document.getElementById('loading');
  const resultsContainer = document.getElementById('results');

  async function getAnalysis(player_name, filter_value) {
    const response = await fetch('https://chessmover-625329947111.us-central1.run.app/api/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        session_hash: "",
        event_id: "",
        data: [
          player_name,
          filter_value
        ],
        event_data: null,
        fn_index: 0,
        trigger_id: 0
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('API Response:', data);
    return data;
  }

  async function waitForResults(player_name, filter_value) {
    const maxAttempts = 10;
    let attempts = 0;

    while (attempts < maxAttempts) {
      const data = await getAnalysis(player_name, filter_value);
      
      if (data && data.data && Array.isArray(data.data)) {
        const [is_generating, status, results] = data.data;
        
        if (!is_generating && results) {
          return { status, results };
        }

        // Update loading message with attempt count
        loadingSpinner.innerHTML = `Analyzing games... (Attempt ${attempts + 1}/${maxAttempts})`;
        
        // Wait 2 seconds before next attempt
        await new Promise(resolve => setTimeout(resolve, 2000));
        attempts++;
      }
    }

    throw new Error('Analysis timed out. Please try again.');
  }

  analyzeButton.addEventListener('click', async () => {
    try {
      const player_name = usernameInput.value.trim();
      const filter_value = filterSelect.value;

      if (!player_name) {
        alert('Please enter a username');
        return;
      }

      loadingSpinner.style.display = 'block';
      loadingSpinner.innerHTML = 'Starting analysis...';
      resultsContainer.innerHTML = '';
      analyzeButton.disabled = true;

      const { status, results } = await waitForResults(player_name, filter_value);

      resultsContainer.innerHTML = `
        <div class="analysis-container">
          <div class="analysis-result">
            <h3>Chess Game Analysis</h3>
            ${status ? `
              <div class="status-message">
                <p><strong>Status:</strong> ${status}</p>
              </div>
            ` : ''}
            <div class="analysis-content">
              ${results}
            </div>
          </div>
        </div>
      `;

    } catch (error) {
      console.error('Analysis error:', error);
      resultsContainer.innerHTML = `
        <div class="error">
          <p>Error: ${error.message}</p>
          <p>Please try again or check the username.</p>
        </div>
      `;
    } finally {
      loadingSpinner.style.display = 'none';
      analyzeButton.disabled = false;
    }
  });
}); 